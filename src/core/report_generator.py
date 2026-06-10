"""
Report generator — produces structured summaries from risk review results.
"""
from __future__ import annotations
from typing import List
from .risk_reviewer import RiskReviewResult


GATE_DECISION_ORDER = [
    "Blocked",
    "Requires Security Review",
    "Requires Architecture Review",
    "Requires QA Review",
    "Needs Clarification",
    "Approved for Development",
]

RISK_LEVEL_ORDER = ["Critical", "High", "Medium", "Low"]


def generate_task_report(task: dict, result: RiskReviewResult) -> dict:
    return {
        "task_id": result.task_id,
        "title": result.task_title,
        "sprint": task.get("sprint", "Unknown"),
        "priority": task.get("priority", "Unknown"),
        "status": task.get("status", "Unknown"),
        "assignee": task.get("assignee", "Unassigned"),
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "gate_decision": result.gate_decision,
        "findings_count": len(result.findings),
        "findings": result.findings,
        "recommendations": result.recommendations,
        "triggered_rules": result.triggered_rules,
    }


def generate_summary_report(task_reports: List[dict]) -> dict:
    total = len(task_reports)
    approved = sum(1 for r in task_reports if r["gate_decision"] == "Approved for Development")
    blocked = sum(1 for r in task_reports if r["gate_decision"] == "Blocked")
    high_risk = sum(1 for r in task_reports if r["risk_level"] in ("High", "Critical"))
    needs_qa = sum(1 for r in task_reports if r["gate_decision"] == "Requires QA Review")
    needs_security = sum(1 for r in task_reports if r["gate_decision"] == "Requires Security Review")
    needs_arch = sum(1 for r in task_reports if r["gate_decision"] == "Requires Architecture Review")
    needs_clarification = sum(1 for r in task_reports if r["gate_decision"] == "Needs Clarification")

    by_risk = {level: sum(1 for r in task_reports if r["risk_level"] == level) for level in RISK_LEVEL_ORDER}
    by_gate = {gate: sum(1 for r in task_reports if r["gate_decision"] == gate) for gate in GATE_DECISION_ORDER}

    return {
        "total_tasks": total,
        "approved_for_development": approved,
        "blocked": blocked,
        "high_risk_or_critical": high_risk,
        "requires_qa_review": needs_qa,
        "requires_security_review": needs_security,
        "requires_architecture_review": needs_arch,
        "needs_clarification": needs_clarification,
        "by_risk_level": by_risk,
        "by_gate_decision": by_gate,
    }
