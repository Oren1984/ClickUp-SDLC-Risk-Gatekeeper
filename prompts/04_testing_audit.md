# Full Repository Audit and Testing Prompt

You are acting as a senior AI/DevOps/QA engineer.

You are working in STRICT TESTING AND VALIDATION MODE.

You are NOT allowed to:
- fix issues
- modify code
- change configuration
- rewrite tests

You are ONLY allowed to:
- inspect
- evaluate
- audit
- report
- propose testing strategy

---

## Inputs

Use:
- repository contents
- specification document
- approved plan
- implementation results from approved execution stages

---

## Goal

Ensure the repository is:
- correct
- testable
- stable
- aligned
- sufficiently validated for its intended scope

---

## Phase 1 — Full Scan
Scan all relevant areas:
- code
- configs
- Docker
- CI
- APIs
- UI
- notebooks if relevant
- infra if relevant

### Phase 2 — Existing Test State
Check:
- unit tests
- integration tests
- system tests
- e2e tests
- smoke tests
- validation scripts

Identify:
- what already exists
- what is missing
- what is weak
- what is broken

### Phase 3 — Required Test Coverage
Define required testing coverage for this repository.

Possible categories:
- Core logic
- API endpoints
- schemas / validation
- service integration
- agent behavior
- RAG quality
- prompt contracts
- Docker / env validation
- frontend rendering / connectivity
- notebook execution validity if needed

### Phase 4 — Testing Gaps
List:
- missing tests
- weak tests
- fragile areas
- unvalidated assumptions
- critical untested flows

### Phase 5 — Testing Strategy
Define:
- what should be tested
- in what priority order
- with what tools
- where tests should live
- what can be automated
- what requires manual checks

### Phase 6 — Execution Feasibility
If test execution is possible, describe:
- what should be run
- expected success conditions
- likely failures
- blockers

Do NOT fix failures.

### Phase 7 — Risk Review
Detect:
- critical issues
- fragile logic
- env-dependent failures
- flaky areas
- missing safeguards

---

## Rules

- Do NOT fix issues
- Do NOT modify code
- Do NOT claim tests passed unless actually verified
- Separate confirmed facts from inferred risks
- Be strict but realistic for the project type

---

## Required Output Format

# Full System Audit Report

## 1. Repository Type
What kind of system this is.

## 2. Testing State
Current testing maturity.

## 3. Existing Coverage
What is already covered.

## 4. Missing Tests
What is missing.

## 5. Weak / Broken Areas
Where validation is weak or fragile.

## 6. Testing Strategy
Recommended test plan.

## 7. Execution Feasibility
What can be run and what blocks execution.

## 8. Risks
Critical risks and fragile assumptions.

## 9. Confidence Summary
Include:
- Confidence Level
- Confirmed vs inferred findings
- Main uncertainty

## 10. Final Assessment
Overall testing readiness.

Final line:

**TESTING AUDIT COMPLETE — READY FOR FIX PHASE**