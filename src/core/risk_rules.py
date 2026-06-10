"""
Risk rules for SDLC task analysis.
Each rule inspects a task dict and returns a finding if triggered.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


SECURITY_KEYWORDS = [
    "auth", "authentication", "login", "password", "oauth", "jwt", "token",
    "encryption", "decrypt", "ssl", "tls", "certificate", "api key", "secret",
    "credential", "access control", "permission", "rbac", "privilege",
    "vulnerability", "injection", "xss", "csrf", "sanitize", "sanitization",
]

AI_KEYWORDS = [
    "llm", "ai", "machine learning", "ml model", "neural network",
    "openai", "gpt", "claude", "gemini", "recommendation engine",
    "content moderation", "automated decision", "chatbot", "nlp",
    "prediction", "inference", "generative",
]

ARCHITECTURE_KEYWORDS = [
    "database", "schema", "migration", "microservice", "api gateway",
    "kubernetes", "docker", "infrastructure", "deployment", "ci/cd",
    "integration", "third-party", "service mesh", "message queue",
    "event driven", "data pipeline", "caching", "load balancer",
    "architecture", "system design",
]

COMPLIANCE_KEYWORDS = [
    "gdpr", "pci", "hipaa", "sox", "compliance", "audit", "regulation",
    "data privacy", "data protection", "legal", "regulatory",
]


@dataclass
class RuleFinding:
    rule_id: str
    severity: str
    weight: int
    finding: str
    recommendation: str


def _text(task: dict, *fields: str) -> str:
    parts = []
    for f in fields:
        val = task.get(f) or ""
        if isinstance(val, list):
            parts.append(" ".join(str(v) for v in val))
        else:
            parts.append(str(val))
    return " ".join(parts).lower()


def _has_keyword(text: str, keywords: list) -> bool:
    for kw in keywords:
        pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
        if re.search(pattern, text):
            return True
    return False


def _is_weak_text(val, min_words: int = 5) -> bool:
    if not val:
        return True
    s = str(val).strip()
    if not s:
        return True
    return len(s.split()) < min_words


def rule_missing_acceptance_criteria(task: dict) -> Optional[RuleFinding]:
    ac = task.get("acceptance_criteria")
    if _is_weak_text(ac, min_words=8):
        return RuleFinding(
            rule_id="RULE-001",
            severity="high",
            weight=20,
            finding="Missing or insufficient acceptance criteria. It is unclear what done means for this task.",
            recommendation="Define clear, testable acceptance criteria with at least 3 specific conditions.",
        )
    return None


def rule_missing_qa_notes(task: dict) -> Optional[RuleFinding]:
    qa = task.get("qa_notes")
    if _is_weak_text(qa, min_words=5):
        return RuleFinding(
            rule_id="RULE-002",
            severity="medium",
            weight=15,
            finding="No QA notes or test plan defined for this task.",
            recommendation="Add QA notes covering test cases, edge cases, and expected behavior.",
        )
    return None


def rule_missing_definition_of_done(task: dict) -> Optional[RuleFinding]:
    dod_status = str(task.get("definition_of_done_status") or "").lower()
    if dod_status in ("", "incomplete", "missing", "not set", "none"):
        return RuleFinding(
            rule_id="RULE-003",
            severity="medium",
            weight=15,
            finding="Definition of Done (DoD) is not confirmed for this task.",
            recommendation="Confirm all DoD items: code reviewed, tests passing, docs updated, deployed to staging.",
        )
    return None


def rule_security_task_without_notes(task: dict) -> Optional[RuleFinding]:
    combined = _text(task, "title", "description", "tags")
    if not _has_keyword(combined, SECURITY_KEYWORDS):
        return None
    sec_notes = task.get("security_notes")
    if _is_weak_text(sec_notes, min_words=5):
        return RuleFinding(
            rule_id="RULE-004",
            severity="critical",
            weight=30,
            finding="Task involves security-sensitive operations but has no security notes or threat model.",
            recommendation="Add security notes covering: threat model, input validation, auth checks, secrets handling, and security test cases.",
        )
    return None


def rule_ai_task_without_guardrails(task: dict) -> Optional[RuleFinding]:
    combined = _text(task, "title", "description", "tags")
    if not _has_keyword(combined, AI_KEYWORDS):
        return None
    qa = str(task.get("qa_notes") or "")
    sec = str(task.get("security_notes") or "")
    arch = str(task.get("architecture_notes") or "")
    guardrail_text = (qa + " " + sec + " " + arch).lower()
    guardrail_keywords = [
        "guardrail", "fallback", "hallucin", "bias", "monitor",
        "rate limit", "human review", "override", "safety", "content filter",
    ]
    if not _has_keyword(guardrail_text, guardrail_keywords):
        return RuleFinding(
            rule_id="RULE-005",
            severity="critical",
            weight=35,
            finding="AI/ML/LLM task lacks guardrails, fallback mechanisms, or safety controls.",
            recommendation="Define output validation guardrails, fallback behavior, bias/safety review, rate limiting, and human-in-the-loop escalation.",
        )
    return None


def rule_architecture_task_without_notes(task: dict) -> Optional[RuleFinding]:
    combined = _text(task, "title", "description", "tags")
    if not _has_keyword(combined, ARCHITECTURE_KEYWORDS):
        return None
    arch_notes = task.get("architecture_notes")
    if _is_weak_text(arch_notes, min_words=8):
        return RuleFinding(
            rule_id="RULE-006",
            severity="high",
            weight=25,
            finding="Task has architectural impact but lacks architecture review or technical design notes.",
            recommendation="Schedule an architecture review. Document system impact, data flow changes, backward compatibility, and rollback plan.",
        )
    return None


def rule_critical_priority_vague_scope(task: dict) -> Optional[RuleFinding]:
    priority = str(task.get("priority") or "").lower()
    if priority != "critical":
        return None
    desc = str(task.get("description") or "")
    ac = str(task.get("acceptance_criteria") or "")
    scope_text = desc + " " + ac
    if len(scope_text.strip().split()) < 20:
        return RuleFinding(
            rule_id="RULE-007",
            severity="high",
            weight=20,
            finding="Critical priority task has vague or minimal scope definition.",
            recommendation="For critical tasks, provide a detailed description, clear acceptance criteria, and explicit success metrics.",
        )
    return None


def rule_blocked_dependency(task: dict) -> Optional[RuleFinding]:
    status = str(task.get("status") or "").lower()
    deps = task.get("dependencies") or []
    if not isinstance(deps, list) or len(deps) == 0:
        return None
    if status in ("blocked", "on hold", "waiting"):
        return RuleFinding(
            rule_id="RULE-008",
            severity="high",
            weight=25,
            finding=f"Task is blocked by unresolved dependencies: {', '.join(str(d) for d in deps)}.",
            recommendation="Resolve blocking dependencies before proceeding. Escalate to PM/Tech Lead if blockers are external.",
        )
    dep_text = _text(task, "description")
    if any(kw in dep_text for kw in ["blocked", "waiting on", "depends on"]):
        return RuleFinding(
            rule_id="RULE-008",
            severity="medium",
            weight=15,
            finding=f"Task has listed dependencies ({', '.join(str(d) for d in deps)}) — confirm they are resolved.",
            recommendation="Verify all dependencies are completed before assigning to development sprint.",
        )
    return None


def rule_compliance_missing_evidence(task: dict) -> Optional[RuleFinding]:
    combined = _text(task, "title", "description", "tags")
    if not _has_keyword(combined, COMPLIANCE_KEYWORDS):
        return None
    sec_notes = str(task.get("security_notes") or "")
    arch_notes = str(task.get("architecture_notes") or "")
    evidence_text = (sec_notes + " " + arch_notes).lower()
    evidence_keywords = [
        "evidence", "audit trail", "log", "dpa", "policy", "certif",
        "signed", "approved", "review completed", "legal sign", "documented",
    ]
    if not _has_keyword(evidence_text, evidence_keywords):
        return RuleFinding(
            rule_id="RULE-009",
            severity="critical",
            weight=35,
            finding="Compliance-related task is missing evidence, audit trail, or regulatory review documentation.",
            recommendation="Attach compliance evidence: DPA signatures, audit logs, policy references, or legal sign-off before development begins.",
        )
    return None


def rule_due_date_risk(task: dict) -> Optional[RuleFinding]:
    due_str = task.get("due_date")
    if not due_str:
        return None
    try:
        due = datetime.strptime(str(due_str), "%Y-%m-%d").date()
        today = date.today()
        delta = (due - today).days
        if delta < 0:
            return RuleFinding(
                rule_id="RULE-010",
                severity="high",
                weight=20,
                finding=f"Task due date ({due_str}) has passed — it is {abs(delta)} day(s) overdue.",
                recommendation="Re-prioritize immediately, update due date, or move to the next sprint with stakeholder approval.",
            )
        if delta <= 3:
            return RuleFinding(
                rule_id="RULE-010",
                severity="medium",
                weight=10,
                finding=f"Task due date ({due_str}) is in {delta} day(s) — at immediate risk of missing deadline.",
                recommendation="Confirm scope is achievable. Consider scope reduction or timeline renegotiation.",
            )
    except (ValueError, TypeError):
        pass
    return None


ALL_RULES = [
    rule_missing_acceptance_criteria,
    rule_missing_qa_notes,
    rule_missing_definition_of_done,
    rule_security_task_without_notes,
    rule_ai_task_without_guardrails,
    rule_architecture_task_without_notes,
    rule_critical_priority_vague_scope,
    rule_blocked_dependency,
    rule_compliance_missing_evidence,
    rule_due_date_risk,
]
