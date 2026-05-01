# AI Project Prompt Pipeline

This folder contains a structured prompt workflow for scanning, planning, reviewing, executing, validating, documenting, and preparing AI engineering repositories.

The prompts are designed to be used in a controlled stage-by-stage process, not all at once.

---

## Workflow Logic

Always start with:

- `00_pipeline_controller.md`

This file defines the global rules, approval flow, phase order, and execution boundaries.

Each working phase is then paired with the controller.

---

## Stage-by-Stage Usage

### Stage 1 — Repository Scan and Planning
Use:

- `00_pipeline_controller.md`
- `01_scan_and_plan.md`

Goal:
- scan the repository
- compare it to the specification
- produce an audit report
- produce a staged execution plan

Expected result:
- repository audit
- cleanup/alignment plan
- execution roadmap

---

### Stage 2 — Architecture Review
Use:

- `00_pipeline_controller.md`
- `02_architecture_review.md`

Goal:
- review repository architecture
- evaluate modularity, boundaries, structure, and scalability
- identify architectural strengths and weaknesses

Expected result:
- architecture review report
- structural improvement recommendations

---

### Stage 3 — Controlled Execution
Use:

- `00_pipeline_controller.md`
- `03_execute_plan.md`

Goal:
- execute only the approved plan
- work one stage at a time
- stop after each completed stage

Expected result:
- controlled implementation progress
- clear per-stage change summary

---

### Stage 4 — Testing Audit
Use:

- `00_pipeline_controller.md`
- `04_testing_audit.md`

Goal:
- inspect repository testing state
- identify missing, weak, or broken validation areas
- define a realistic testing strategy

Expected result:
- testing audit report
- fix-phase readiness

---

### Stage 5 — Documentation Audit and Planning
Use:

- `00_pipeline_controller.md`
- `05_documentation_update.md`

Goal:
- review documentation quality and alignment
- detect outdated, missing, or duplicated docs
- define documentation update direction

Expected result:
- documentation update plan
- doc structure improvement guidance

---

### Stage 6 — CI/CD and Delivery Planning
Use:

- `00_pipeline_controller.md`
- `06_cicd_setup.md`

Goal:
- review build, test, and deployment readiness
- define CI/CD structure appropriate to the project
- identify gaps and delivery blockers

Expected result:
- CI/CD plan
- deployment readiness direction

---

## Practical Usage Flow

### Step 1
Give the agent:

- `00_pipeline_controller.md`
- `01_scan_and_plan.md`

Get:
- audit report
- work plan

Then:
- review
- approve

---

### Step 2
Give the agent:

- `00_pipeline_controller.md`
- `02_architecture_review.md`

Get:
- architecture review

Then:
- review
- approve

---

### Step 3
Give the agent:

- `00_pipeline_controller.md`
- `03_execute_plan.md`

Get:
- controlled execution of one approved stage at a time

Then:
- review
- approve each stage before continuing

---

### Step 4
Give the agent:

- `00_pipeline_controller.md`
- `04_testing_audit.md`

Get:
- testing and validation report

Then:
- review
- decide what to fix

---

### Step 5
Give the agent:

- `00_pipeline_controller.md`
- `05_documentation_update.md`

Get:
- documentation update plan

Then:
- review
- approve

---

### Step 6
Give the agent:

- `00_pipeline_controller.md`
- `06_cicd_setup.md`

Get:
- CI/CD and delivery plan

Then:
- review
- approve

---

## Important Rule

Do not run all prompts together.

Use them as a staged operating system for repository work:
1. analyze
2. review architecture
3. execute
4. validate
5. align documentation
6. prepare delivery flow

---

## Suggested File Order

```text
00_pipeline_controller.md
01_scan_and_plan.md
02_architecture_review.md
03_execute_plan.md
04_testing_audit.md
05_documentation_update.md
06_cicd_setup.md
```

---

## Purpose of This Folder

This prompt system is intended to help AI agents work in a more disciplined, reviewable, and production-like way across real repositories, templates, and AI engineering systems.

---
