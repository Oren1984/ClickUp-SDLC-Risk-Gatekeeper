"""Tests for compliance check module."""
import pytest
from src.core.compliance_checks import check_compliance, has_compliance_gaps


def _task(**kwargs):
    base = {
        "task_id": "TEST-001",
        "title": "Test task",
        "description": "A plain test task.",
        "tags": [],
        "security_notes": None,
        "architecture_notes": None,
        "qa_notes": None,
    }
    base.update(kwargs)
    return base


def test_no_compliance_keywords_returns_empty():
    task = _task(title="Fix button color", description="Change button from blue to green.")
    results = check_compliance(task)
    assert results == []


def test_gdpr_task_triggers_gdpr():
    task = _task(title="Implement GDPR data deletion", tags=["gdpr", "compliance"])
    results = check_compliance(task)
    frameworks = [r.framework for r in results]
    assert "GDPR" in frameworks


def test_gdpr_with_evidence_no_gap():
    task = _task(
        title="GDPR data deletion endpoint",
        tags=["gdpr"],
        security_notes="DPA signed. Data retention policy documented. Legal basis confirmed.",
    )
    results = check_compliance(task)
    gdpr_results = [r for r in results if r.framework == "GDPR"]
    assert len(gdpr_results) == 1
    assert gdpr_results[0].has_evidence is True
    assert gdpr_results[0].gap_description is None


def test_gdpr_without_evidence_has_gap():
    task = _task(title="Delete user data for GDPR compliance", tags=["gdpr"])
    results = check_compliance(task)
    gdpr_results = [r for r in results if r.framework == "GDPR"]
    assert len(gdpr_results) == 1
    assert gdpr_results[0].has_evidence is False
    assert gdpr_results[0].gap_description is not None
    assert gdpr_results[0].action_required is not None


def test_pci_task_triggers_pci():
    task = _task(title="Integrate payment gateway", tags=["payment", "pci"])
    results = check_compliance(task)
    frameworks = [r.framework for r in results]
    assert "PCI-DSS" in frameworks


def test_has_compliance_gaps_true():
    task = _task(title="GDPR compliance task", tags=["gdpr"])
    assert has_compliance_gaps(task) is True


def test_has_compliance_gaps_false_with_evidence():
    task = _task(
        title="GDPR data request endpoint",
        tags=["gdpr"],
        security_notes="DPA contract signed. Privacy policy updated. Legal basis: contract.",
    )
    assert has_compliance_gaps(task) is False


def test_multiple_frameworks_detected():
    task = _task(
        title="Encrypt PII for GDPR and PCI compliance",
        description="Handle payment and personal data.",
        tags=["gdpr", "pci", "encryption"],
    )
    results = check_compliance(task)
    frameworks = {r.framework for r in results}
    assert "GDPR" in frameworks
    assert "PCI-DSS" in frameworks
