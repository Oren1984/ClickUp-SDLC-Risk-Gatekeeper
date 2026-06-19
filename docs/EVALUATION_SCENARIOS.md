# Evaluation Scenarios

**ClickUp SDLC Risk Gatekeeper**

These scenarios demonstrate the range of risk detection and decision-support capabilities of the system. Each scenario includes the input task summary, the risk the system detects, the expected AI output, the expected human decision, and why the scenario matters in real software delivery.

---

## Scenario 1 — User Story Missing Acceptance Criteria

**Input task summary:**
> Task: "Add user login with Google OAuth"
> Description: "Users should be able to log in using their Google account."
> Acceptance Criteria: *(empty)*
> Priority: High | Tags: auth, backend

**Risk detected:**
- RULE-001: Acceptance criteria missing
- RULE-004: Auth task with no security notes
- RULE-003: DoD not confirmed

**Expected AI output:**
- Risk Score: 65/100 — High
- Gate Decision: Requires Security Review
- Findings: Missing acceptance criteria; no security notes for an auth task; DoD not confirmed
- Recommendations: Define success/failure scenarios for OAuth flow; document token handling and session expiry; confirm DoD checklist

**Expected human decision:**
PM updates acceptance criteria (e.g., "User can authenticate with Google, session token is issued with 24h expiry, invalid token returns 401"), security lead adds threat model notes. Task re-submits and clears to Approved.

**Why this matters:**
Missing acceptance criteria on auth tasks is a common root cause of security rework. A developer implementing OAuth without a defined success state may make assumptions about token storage, expiry handling, or logout behaviour that later require costly fixes.

---

## Scenario 2 — Task with Unclear Definition of Done

**Input task summary:**
> Task: "Deploy Sprint 4 to Production"
> Description: "Deploy."
> Acceptance Criteria: *(empty)*
> Priority: Critical | DoD Status: incomplete

**Risk detected:**
- RULE-001: Acceptance criteria missing or too vague
- RULE-002: No QA notes
- RULE-003: DoD not confirmed
- RULE-007: Critical priority with insufficient scope

**Expected AI output:**
- Risk Score: 70/100 — High
- Gate Decision: Needs Clarification
- Findings: One-word description provides no scope; no acceptance criteria; no QA or smoke test plan; DoD incomplete for a critical deployment
- Recommendations: Define go/no-go criteria, rollback plan, smoke test steps, and stakeholder sign-off requirement

**Expected human decision:**
PM expands description to include rollback plan, smoke test checklist, deployment window, and go/no-go gate. QA adds post-deploy verification steps. Task re-submits and clears.

**Why this matters:**
Production deployments with no defined success criteria are one of the highest-risk events in SDLC. A "deploy" task with nothing documented is a sprint liability waiting to become an incident.

---

## Scenario 3 — High-Priority Bug with No Reproduction Steps

**Input task summary:**
> Task: "Fix checkout crash on mobile"
> Description: "App crashes when checking out on mobile."
> Acceptance Criteria: "It should not crash."
> Priority: Critical | QA Notes: *(empty)*

**Risk detected:**
- RULE-001: Acceptance criteria insufficient (no specific condition, trigger, or observable outcome)
- RULE-002: No QA notes or test plan

**Expected AI output:**
- Risk Score: 35/100 — Medium
- Gate Decision: Requires QA Review
- Findings: Acceptance criteria do not specify reproduction steps, device, OS, or expected outcome; no QA notes with regression scope
- Recommendations: Add repro steps (device, OS version, cart state); define regression test scope to prevent recurrence

**Expected human decision:**
QA lead adds reproduction steps (iPhone 13, iOS 17, items in cart, guest checkout flow) and regression test scope. Acceptance criteria updated to specify exact expected checkout flow. Task clears.

**Why this matters:**
Bugs without reproduction steps are frequently misunderstood, fixed incorrectly, or reintroduced. Clear QA criteria prevent the "fixed on my machine" pattern.

---

## Scenario 4 — Feature Request with Security Implications

**Input task summary:**
> Task: "Add file upload feature for user avatars"
> Description: "Users can upload a profile picture."
> Tags: backend, storage
> Security Notes: *(empty)*
> Acceptance Criteria: "Upload works."

**Risk detected:**
- RULE-001: Acceptance criteria too vague
- RULE-004: Task involves file upload (implicit security concern) with no security notes

**Expected AI output:**
- Risk Score: 50/100 — Medium
- Gate Decision: Requires Security Review
- Findings: File upload features require security notes (file type validation, size limits, storage security, malware scanning); acceptance criteria do not define allowed file types or size limits
- Recommendations: Add security notes covering allowed types (JPEG/PNG only), max file size, storage bucket access control, and virus scan requirement

**Expected human decision:**
Security lead adds notes covering file type whitelist, 5MB size limit, S3 bucket policy, and Clam AV scan step. Acceptance criteria updated to specify allowed types and max dimensions. Task re-submits and clears.

**Why this matters:**
File upload features are a common attack vector (unrestricted upload, path traversal, stored XSS). A task that doesn't document security controls is very likely to ship without them.

---

## Scenario 5 — Task Blocked by External Dependency

**Input task summary:**
> Task: "Refactor GraphQL API to use new user schema"
> Status: blocked
> Dependencies: [TASK-003 — Database Schema Migration]
> Priority: High

**Risk detected:**
- RULE-008: Task is blocked by an unresolved dependency

**Expected AI output:**
- Risk Score: 25/100 — Low (but gate is overridden)
- Gate Decision: Blocked
- Findings: Task status is 'blocked'; depends on TASK-003 which has not been completed
- Recommendations: Do not assign to a developer until TASK-003 is resolved; remove from active sprint; track as sprint risk

**Expected human decision:**
PM removes task from active sprint or places it in a dependency queue. Task is re-evaluated after TASK-003 closes.

**Why this matters:**
Assigning a developer to a blocked task wastes sprint capacity and creates interruptions. Explicit dependency visibility prevents this pattern before it reaches the daily standup.

---

## Scenario 6 — QA Coverage Missing

**Input task summary:**
> Task: "Add admin role management to user settings"
> Description: "Admins can assign and revoke roles from users in the settings panel."
> QA Notes: *(empty)*
> DoD Status: incomplete

**Risk detected:**
- RULE-002: No QA notes or test plan
- RULE-003: DoD not confirmed

**Expected AI output:**
- Risk Score: 30/100 — Medium
- Gate Decision: Requires QA Review
- Findings: No QA notes for a role management feature with security implications; DoD not confirmed
- Recommendations: Define test cases for role assignment, revocation, permission boundary validation, and unauthorised access attempts

**Expected human decision:**
QA lead adds test cases: valid role assignment, role revocation, privilege escalation attempt (should fail), and UI state after role change. DoD confirmed. Task clears.

**Why this matters:**
Role management without explicit QA coverage is a reliable path to privilege escalation bugs. Test cases define the expected behaviour for both the happy path and the adversarial path.

---

## Scenario 7 — Sprint Item Too Large or Vague

**Input task summary:**
> Task: "Implement search functionality"
> Description: "Search."
> Priority: Critical
> Acceptance Criteria: *(empty)*
> Sprint: Sprint 3

**Risk detected:**
- RULE-001: Acceptance criteria missing
- RULE-002: No QA notes
- RULE-003: DoD not confirmed
- RULE-007: Critical priority task with vague (one-word) scope

**Expected AI output:**
- Risk Score: 70/100 — High
- Gate Decision: Needs Clarification
- Findings: One-word description and empty acceptance criteria for a critical task make scope undefined; no QA plan; DoD not set
- Recommendations: Break down into specific sub-tasks or user stories; define search scope (which entities, which fields, what ranking); set acceptance criteria per story

**Expected human decision:**
PM breaks into sub-tasks (e.g., product search by name, filter by category, search result ranking). Each sub-task gets its own acceptance criteria, QA plan, and DoD. The original vague task is closed.

**Why this matters:**
Vague critical tasks are a sprint planning anti-pattern. They enter development with undefined scope, expand mid-sprint, and cause missed commitments.

---

## Scenario 8 — Compliance-Sensitive Change Without Review Notes

**Input task summary:**
> Task: "Implement GDPR right-to-erasure endpoint"
> Description: "Add API endpoint to delete all user data on request."
> Tags: gdpr, compliance
> Security Notes: *(empty)*
> Acceptance Criteria: "Delete user data."

**Risk detected:**
- RULE-009: Compliance task with no evidence or regulatory documentation
- RULE-001: Acceptance criteria too vague
- RULE-004: No security notes for a data deletion endpoint

**Expected AI output:**
- Risk Score: 85/100 — Critical
- Gate Decision: Requires Security Review
- Findings: GDPR erasure task missing evidence, DPA reference, audit trail requirement, and cascade deletion scope; acceptance criteria do not define which data is deleted; no security notes for a privileged endpoint
- Recommendations: Add legal/DPA reference; document which tables and services are included in erasure; define audit log requirement; add security notes for endpoint access control and rate limiting

**Expected human decision:**
Legal confirms DPA reference. Engineering defines erasure scope (user profile, orders, sessions, analytics). Security adds endpoint auth requirement and rate limit. Acceptance criteria updated with specific data scope and audit log requirement. Task re-submits.

**Why this matters:**
GDPR right-to-erasure implementations without documented evidence and explicit scope are a compliance liability. Missing cascade deletions or audit trails are the most common failure mode.

---

## Scenario 9 — Production Fix Missing Rollback Plan

**Input task summary:**
> Task: "Hotfix: Revert payment webhook handler to v1"
> Description: "The v2 webhook handler is causing duplicate charge events. Revert to v1 handler immediately."
> Priority: Critical
> Tags: hotfix, payments
> Security Notes: *(empty)*
> Acceptance Criteria: "Revert the handler."

**Risk detected:**
- RULE-001: Acceptance criteria do not define success state or verification step
- RULE-004: Payment-related task with no security notes
- RULE-007: Critical priority with insufficient scope (no rollback plan, no verification criteria)

**Expected AI output:**
- Risk Score: 70/100 — High
- Gate Decision: Needs Clarification
- Findings: Hotfix missing rollback plan; no success verification criteria; no security/audit notes for a payment handler change
- Recommendations: Define pre-deploy verification step; define rollback trigger condition; add monitoring checkpoint; document who approves the hotfix deployment

**Expected human decision:**
PM adds hotfix checklist: verify duplicate charges stopped in staging, confirm idempotency key handling, document rollback trigger (>1 duplicate per hour), add monitoring alert. Tech Lead signs off. Task re-submits and clears.

**Why this matters:**
Production hotfixes applied without a rollback plan or verification step are themselves a risk. In payment systems, an incomplete fix can cause additional incidents. The gate prevents "fix on the fly" from becoming "second incident."

---

## Scenario 10 — Task Ready for Development After Proper Clarification

**Input task summary:**
> Task: "Update password hashing to bcrypt (replace MD5)"
> Description: "Replace all MD5 password hashes with bcrypt (cost factor 12). Migrate existing hashes on first login."
> Acceptance Criteria: "All new passwords use bcrypt cost factor 12. Legacy MD5 hashes are migrated on first successful login. No plaintext passwords in logs. CISO sign-off obtained."
> Security Notes: "Reviewed by CISO. bcrypt cost factor 12 confirmed. Migration strategy approved. Logs audited to confirm no plaintext exposure."
> QA Notes: "Unit tests cover hash generation, verification, and migration path. Integration test confirms login with migrated hash."
> DoD Status: complete
> Tags: security, auth

**Risk detected:**
- None — all rules pass

**Expected AI output:**
- Risk Score: 0/100 — Low
- Gate Decision: ✅ Approved for Development
- Findings: None
- Recommendations: None

**Expected human decision:**
Task is approved and enters the sprint.

**Why this matters:**
This scenario demonstrates what a well-prepared task looks like. Clear acceptance criteria, documented security review, CISO reference, QA plan, and complete DoD — the gate has nothing to flag. This is the target state for all tasks before development starts.
