# Demo Scenarios

This document walks through the 20 mock tasks and explains what each one demonstrates.

---

## Critical Risk Tasks

### TASK-002 — AI Recommendation Engine (Critical)
**Why it's Critical:** AI/LLM task with no guardrails, no QA notes, no DoD.
**Rules triggered:** RULE-002, RULE-003, RULE-005, RULE-007
**Gate:** Requires Security Review
**Demo point:** AI features need more than just implementation — they need safety controls, fallback behavior, and bias checks defined before development starts.

### TASK-005 — Stripe Payment Integration (Critical)
**Why it's Critical:** PCI-DSS compliance task with no acceptance criteria, no QA, no security notes, no evidence.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-004, RULE-009
**Gate:** Requires Security Review
**Demo point:** Payment tasks are high-stakes. Missing PCI evidence is a compliance blocker.

### TASK-013 — LLM Content Moderation (Critical)
**Why it's Critical:** AI task with no acceptance criteria, no security notes, no DoD, no guardrails.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-005, RULE-007
**Gate:** Requires Security Review
**Demo point:** LLM moderation systems need content filters, human review escalation paths, and fallback defined before coding.

### TASK-018 — Data Encryption at Rest (Critical)
**Why it's Critical:** Combines security + GDPR + PCI + database architecture with nothing defined.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-004, RULE-006, RULE-009
**Gate:** Requires Security Review
**Demo point:** Multi-concern tasks accumulate risk quickly. Each gap adds to the score.

---

## High Risk Tasks

### TASK-001 — OAuth2 Authentication (High)
**Why it's High:** Auth task with no acceptance criteria, no security notes, no QA, incomplete DoD.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-004
**Gate:** Requires Security Review
**Demo point:** Authentication tasks always need security review regardless of how familiar the implementation seems.

### TASK-003 — Database Schema Migration (High)
**Why it's High:** Database migration with no architecture notes.
**Rules triggered:** RULE-003, RULE-006
**Gate:** Requires Architecture Review
**Demo point:** Schema migrations have wide blast radius. Architecture review is mandatory.

### TASK-007 — Deploy Sprint 4 to Production (High)
**Why it's High:** Critical priority deployment with description "Deploy." — vague scope, no DoD.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-007
**Gate:** Needs Clarification
**Demo point:** Deployment tasks need explicit rollback plans, smoke test criteria, and go/no-go gates.

### TASK-012 — CI/CD Pipeline Setup (High)
**Why it's High:** CI/CD infrastructure change without architecture notes.
**Rules triggered:** RULE-003, RULE-006
**Gate:** Requires Architecture Review

### TASK-015 — Search Feature (High)
**Why it's High:** Critical priority task with description "Search." — extreme vague scope.
**Rules triggered:** RULE-001, RULE-002, RULE-003, RULE-007
**Gate:** Needs Clarification
**Demo point:** Even simple-looking tasks need proper scoping when marked critical.

---

## Compliance Gaps

### TASK-008 — GDPR Data Deletion (Critical gap)
**Compliance gap:** GDPR task with no documentation, no DPA reference, no audit trail.
**Gate:** Requires Security Review
**Demo point:** Legal compliance requires documented evidence, not just code.

---

## Blocked Tasks

### TASK-009 — GraphQL Refactor (Blocked)
**Why it's Blocked:** Status = blocked, depends on TASK-003 (schema migration).
**Gate:** Blocked
**Demo point:** Dependency management is a real sprint-planning risk. Blocked tasks should never enter active development.

---

## Medium Risk Tasks

### TASK-011 — Admin Dashboard (Medium)
**Gap:** No QA notes defined despite security-relevant RBAC feature.
**Gate:** Requires QA Review

### TASK-017 — Analytics SDK Integration (Medium)
**Gap:** No acceptance criteria.
**Gate:** Needs Clarification

---

## Low Risk Tasks (Approved)

### TASK-004 — Fix Typo on About Page
Clean task: good AC, complete DoD, proper QA notes, no security impact.
**Gate:** Approved for Development ✅

### TASK-006 — Unit Tests for Order Service
Well-defined testing task with full DoD and QA plan.
**Gate:** Approved for Development ✅

### TASK-010 — Rate Limiting on API Gateway
Security task with proper security notes, architecture notes, and QA plan.
**Gate:** Approved for Development ✅

### TASK-014 — bcrypt Password Hashing
Security task with complete security notes including CISO sign-off reference.
**Gate:** Approved for Development ✅

### TASK-016 — Performance Testing (Checkout)
Well-scoped QA task with complete DoD and test methodology.
**Gate:** Approved for Development ✅

### TASK-019 — Fix Mobile Image Loading
Clear bug fix with scope, acceptance criteria, and QA notes.
**Gate:** Approved for Development ✅

---

## Summary of Coverage

| Scenario | Task(s) |
|----------|---------|
| Missing acceptance criteria | TASK-001, 005, 007, 013, 015 |
| No QA plan | TASK-001, 002, 005, 007, 011, 013, 020 |
| Security task without notes | TASK-001, 005, 018 |
| AI/LLM without guardrails | TASK-002, 013 |
| Architecture impact without review | TASK-003, 012, 020 |
| Critical priority vague scope | TASK-007, 015 |
| Blocked by dependency | TASK-009 |
| Compliance missing evidence | TASK-005, 008, 018 |
| Task approved and ready | TASK-004, 006, 010, 014, 016, 019 |
