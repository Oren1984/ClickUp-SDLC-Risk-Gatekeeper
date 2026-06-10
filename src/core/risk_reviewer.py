"""
RiskReviewer: applies all rules to a task and produces a structured review result.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .risk_rules import ALL_RULES, RuleFinding


@dataclass
class RiskReviewResult:
    task_id: str
    task_title: str
    risk_score: int
    risk_level: str
    gate_decision: str
    findings: List[str]
    recommendations: List[str]
    triggered_rules: List[str]


def _score_to_level(score: int) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Medium"
    if score <= 75:
        return "High"
    return "Critical"


def _determine_gate(findings: list[RuleFinding], risk_level: str) -> str:
    rule_ids = {f.rule_id for f in findings}

    if "RULE-008" in rule_ids and any(
        f.rule_id == "RULE-008" and f.severity == "high" for f in findings
    ):
        return "Blocked"

    SECURITY_RULES = {"RULE-004", "RULE-005", "RULE-009"}
    if risk_level in ("Critical", "High"):
        if rule_ids & SECURITY_RULES:
            return "Requires Security Review"
        if "RULE-006" in rule_ids:
            return "Requires Architecture Review"
        if "RULE-002" in rule_ids:
            return "Requires QA Review"
        return "Needs Clarification"

    if risk_level == "Medium":
        if rule_ids & SECURITY_RULES:
            return "Requires Security Review"
        if "RULE-006" in rule_ids:
            return "Requires Architecture Review"
        if "RULE-002" in rule_ids:
            return "Requires QA Review"
        return "Needs Clarification"

    return "Approved for Development"


class RiskReviewer:
    def review(self, task: dict) -> RiskReviewResult:
        triggered: list[RuleFinding] = []
        for rule_fn in ALL_RULES:
            result = rule_fn(task)
            if result is not None:
                triggered.append(result)

        raw_score = sum(f.weight for f in triggered)
        risk_score = min(raw_score, 100)
        risk_level = _score_to_level(risk_score)
        gate_decision = _determine_gate(triggered, risk_level)

        return RiskReviewResult(
            task_id=task.get("task_id", "UNKNOWN"),
            task_title=task.get("title", "Untitled"),
            risk_score=risk_score,
            risk_level=risk_level,
            gate_decision=gate_decision,
            findings=[f.finding for f in triggered],
            recommendations=[f.recommendation for f in triggered],
            triggered_rules=[f.rule_id for f in triggered],
        )

    def review_all(self, tasks: list) -> list[RiskReviewResult]:
        return [self.review(t) for t in tasks]
