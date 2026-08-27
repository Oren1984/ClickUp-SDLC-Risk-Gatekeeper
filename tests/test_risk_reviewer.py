"""Tests for the risk reviewer — scoring, levels, and gate decisions."""
import pytest
from src.core.risk_reviewer import RiskReviewer, RiskReviewResult, _score_to_level


@pytest.fixture
def reviewer():
    return RiskReviewer()


def _task(**kwargs):
    base = {
        "task_id": "TEST-001",
        "title": "Test task",
        "description": "A test task with enough detail to avoid false positives.",
        "status": "Ready for Development",
        "priority": "medium",
        "assignee": "Tester",
        "sprint": "Sprint 1",
        "tags": [],
        "acceptance_criteria": "Given a valid input, when the action is taken, then the expected outcome occurs with no errors.",
        "definition_of_done_status": "complete",
        "security_notes": None,
        "architecture_notes": None,
        "qa_notes": "Unit tests cover happy path and edge cases. Regression tests run in CI.",
        "risk_level": None,
        "dependencies": [],
        "due_date": None,
    }
    base.update(kwargs)
    return base


class TestScoreToLevel:
    def test_low(self):
        assert _score_to_level(0) == "Low"
        assert _score_to_level(25) == "Low"

    def test_medium(self):
        assert _score_to_level(26) == "Medium"
        assert _score_to_level(50) == "Medium"

    def test_high(self):
        assert _score_to_level(51) == "High"
        assert _score_to_level(75) == "High"

    def test_critical(self):
        assert _score_to_level(76) == "Critical"
        assert _score_to_level(100) == "Critical"


class TestRiskReviewerApproved:
    def test_clean_task_approved(self, reviewer):
        task = _task()
        result = reviewer.review(task)
        assert isinstance(result, RiskReviewResult)
        assert result.risk_level == "Low"
        assert result.gate_decision == "Approved for Development"
        assert len(result.findings) == 0

    def test_review_all_returns_list(self, reviewer):
        tasks = [_task(task_id=f"T-{i:03d}") for i in range(5)]
        results = reviewer.review_all(tasks)
        assert len(results) == 5
        assert all(isinstance(r, RiskReviewResult) for r in results)


class TestMissingAcceptanceCriteria:
    def test_no_acceptance_criteria_triggers(self, reviewer):
        task = _task(acceptance_criteria=None)
        result = reviewer.review(task)
        assert "RULE-001" in result.triggered_rules

    def test_weak_acceptance_criteria_triggers(self, reviewer):
        task = _task(acceptance_criteria="It works.")
        result = reviewer.review(task)
        assert "RULE-001" in result.triggered_rules

    def test_good_acceptance_criteria_passes(self, reviewer):
        task = _task(acceptance_criteria="User can log in with valid credentials and receives a JWT token with correct expiry.")
        result = reviewer.review(task)
        assert "RULE-001" not in result.triggered_rules


class TestMissingQANotes:
    def test_no_qa_notes_triggers(self, reviewer):
        task = _task(qa_notes=None)
        result = reviewer.review(task)
        assert "RULE-002" in result.triggered_rules

    def test_good_qa_notes_passes(self, reviewer):
        task = _task(qa_notes="Unit tests cover all methods. Integration test verifies API contract.")
        result = reviewer.review(task)
        assert "RULE-002" not in result.triggered_rules


class TestSecurityRule:
    def test_auth_task_without_security_notes_triggers(self, reviewer):
        task = _task(
            title="Implement OAuth2 authentication",
            tags=["auth", "backend"],
            security_notes=None,
        )
        result = reviewer.review(task)
        assert "RULE-004" in result.triggered_rules

    def test_auth_task_with_security_notes_passes(self, reviewer):
        task = _task(
            title="Update authentication middleware",
            tags=["auth"],
            security_notes="JWT tokens validated on every request. No secrets in logs. Expiry enforced.",
        )
        result = reviewer.review(task)
        assert "RULE-004" not in result.triggered_rules


class TestAIGuardrailRule:
    def test_llm_task_without_guardrails_triggers(self, reviewer):
        task = _task(
            title="Add LLM chatbot feature",
            tags=["llm", "ai"],
            qa_notes=None,
            security_notes=None,
            architecture_notes=None,
        )
        result = reviewer.review(task)
        assert "RULE-005" in result.triggered_rules

    def test_ai_task_with_guardrails_passes(self, reviewer):
        task = _task(
            title="Add AI recommendation feature",
            tags=["ai", "ml model"],
            qa_notes="Content filter guardrail applied to all outputs. Fallback to rule-based if AI fails. Human review for flagged items.",
        )
        result = reviewer.review(task)
        assert "RULE-005" not in result.triggered_rules

    def test_ai_readiness_finding_lists_all_dimensions(self, reviewer):
        task = _task(
            title="Add LLM chatbot feature",
            tags=["llm", "ai"],
            qa_notes=None,
            security_notes=None,
            architecture_notes=None,
        )
        result = reviewer.review(task)
        finding_text = " ".join(result.findings + result.recommendations).lower()
        for dimension in (
            "evaluation criteria",
            "groundedness",
            "cost",
            "fallback",
            "tool/data permission",
            "guardrail",
        ):
            assert dimension in finding_text

    def test_ai_task_with_partial_readiness_notes_still_passes(self, reviewer):
        task = _task(
            title="Add AI recommendation feature",
            tags=["ai", "ml model"],
            qa_notes="Least privilege data access only; no write scopes granted to the model.",
        )
        result = reviewer.review(task)
        assert "RULE-005" not in result.triggered_rules


class TestArchitectureRule:
    def test_database_task_without_arch_notes_triggers(self, reviewer):
        task = _task(
            title="Database schema migration",
            tags=["database", "migration"],
            architecture_notes=None,
        )
        result = reviewer.review(task)
        assert "RULE-006" in result.triggered_rules


class TestBlockedDependency:
    def test_blocked_status_with_deps_triggers(self, reviewer):
        task = _task(
            status="blocked",
            dependencies=["TASK-003"],
        )
        result = reviewer.review(task)
        assert "RULE-008" in result.triggered_rules
        assert result.gate_decision == "Blocked"

    def test_no_deps_no_trigger(self, reviewer):
        task = _task(dependencies=[])
        result = reviewer.review(task)
        assert "RULE-008" not in result.triggered_rules


class TestGateDecisions:
    def test_blocked_task_gate(self, reviewer):
        task = _task(status="blocked", dependencies=["TASK-099"])
        result = reviewer.review(task)
        assert result.gate_decision == "Blocked"

    def test_risk_score_capped_at_100(self, reviewer):
        task = _task(
            title="OAuth2 authentication with LLM AI encryption GDPR compliance",
            description="x",
            tags=["auth", "llm", "gdpr", "pci"],
            acceptance_criteria=None,
            qa_notes=None,
            security_notes=None,
            architecture_notes=None,
            definition_of_done_status="missing",
            priority="critical",
        )
        result = reviewer.review(task)
        assert result.risk_score <= 100
