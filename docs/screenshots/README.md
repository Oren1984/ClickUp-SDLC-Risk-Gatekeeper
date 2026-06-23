## ClickUp Demo Workspace

This project includes a practical ClickUp demo workspace that shows how the SDLC Risk Gatekeeper can be represented inside a real project-management tool.

The ClickUp workspace was created as a live portfolio demonstration for the project:

**Workspace:** Oren Project Systems
**Space:** ClickUp SDLC Risk Gatekeeper
**Folder:** Risk Gate Demo

The demo structure includes five lists:

1. Backlog & Requirements
2. SDLC Risk Review
3. QA / DoD Validation
4. Governance & HITL
5. Demo Dashboard

The goal of the ClickUp workspace is to show how software-delivery risks can be organized visually across backlog review, SDLC risk detection, QA/DoD validation, human review, and executive-level dashboard views.

### Demo Workflow

The ClickUp demo follows the same SDLC positioning as the project logic:

```text
Backlog → Sprint Planning → SDLC Risk Gate → Human Review → Development Approval

Example task groups include:

Authentication and OAuth2 risk review
AI/LLM feature safety and guardrail review
Stripe / PCI-DSS payment integration review
Database schema migration architecture review
GraphQL dependency blocker tracking
QA / Definition of Done validation
Human-in-the-loop security, QA, and tech-lead review

The ClickUp board is not connected to the live ClickUp API in this version. It is a manual live workspace demonstration that mirrors the project’s mock-first architecture and future integration readiness.

ClickUp Demo Screenshots

Screenshots are stored under:

docs/screenshots/

Included screenshots:

01-clickup-risk-gate-demo-dashboard-overview.png
02-clickup-risk-gate-dashboard-priority-overview.png
03-clickup-risk-gate-folder-structure-progress.png
1. Dashboard Overview

Shows the ClickUp dashboard view created for the SDLC Risk Gatekeeper demo, including executive summary, workload status, completed task count, and general dashboard widgets.

2. Priority Overview

Shows the dashboard priority overview for the main risk categories:

Critical Risks Overview
Security Review Queue
Blocked Tasks Overview
Approved Tasks Overview

The priority flags demonstrate how project risks can be visually separated by urgency.

3. Folder Structure and Progress

Shows the ClickUp folder/list structure and progress tracking across the full demo workspace:

SDLC Risk Review
Backlog & Requirements
QA / DoD Validation
Governance & HITL
Demo Dashboard

Demo Positioning

This ClickUp workspace demonstrates how the project can be mapped into a real project-management workflow without requiring live API credentials.

Current state:

Mock-first project architecture
No live ClickUp API calls
No credentials stored in the repository
Manual ClickUp workspace created for portfolio demonstration
Future API readiness documented separately

The purpose of this demo is to show the business and project-management layer around the SDLC Risk Gatekeeper: how risks, review queues, blockers, QA gaps, and human approvals can be surfaced inside a familiar delivery-management tool.
