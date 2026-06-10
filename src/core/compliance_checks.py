"""
Compliance-specific checks for SDLC tasks.
Detects GDPR, PCI, HIPAA, SOX, and general security compliance gaps.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


COMPLIANCE_PROFILES = {
    "GDPR": {
        "keywords": ["gdpr", "data privacy", "right to erasure", "consent", "data subject", "personal data"],
        "required_evidence": ["data protection impact", "dpia", "dpa", "privacy policy", "legal basis", "data retention"],
        "description": "EU General Data Protection Regulation",
    },
    "PCI-DSS": {
        "keywords": ["pci", "payment", "card", "cardholder", "credit card", "debit card", "payment gateway"],
        "required_evidence": ["pci compliant", "tokeniz", "encryption", "vault", "masked", "no raw card"],
        "description": "Payment Card Industry Data Security Standard",
    },
    "HIPAA": {
        "keywords": ["hipaa", "health data", "medical record", "patient", "phi", "ehr", "emr"],
        "required_evidence": ["phi", "hipaa", "business associate", "audit log", "access control", "encrypted"],
        "description": "Health Insurance Portability and Accountability Act",
    },
    "SOX": {
        "keywords": ["sox", "sarbanes", "financial report", "audit trail", "financial control"],
        "required_evidence": ["audit trail", "change log", "approved", "segregation of duties", "sox control"],
        "description": "Sarbanes-Oxley Act",
    },
    "GENERAL_SECURITY": {
        "keywords": ["security", "vulnerability", "penetration", "pen test", "owasp", "cve"],
        "required_evidence": ["security review", "pentest", "owasp", "approved", "remediated", "risk accepted"],
        "description": "General security compliance",
    },
}


@dataclass
class ComplianceResult:
    framework: str
    description: str
    triggered: bool
    has_evidence: bool
    gap_description: Optional[str]
    action_required: Optional[str]


def check_compliance(task: dict) -> List[ComplianceResult]:
    combined = " ".join([
        str(task.get("title") or ""),
        str(task.get("description") or ""),
        " ".join(task.get("tags") or []),
    ]).lower()

    evidence_text = " ".join([
        str(task.get("security_notes") or ""),
        str(task.get("architecture_notes") or ""),
        str(task.get("qa_notes") or ""),
    ]).lower()

    results = []
    for framework, profile in COMPLIANCE_PROFILES.items():
        triggered = any(kw in combined for kw in profile["keywords"])
        if not triggered:
            continue
        has_evidence = any(ev in evidence_text for ev in profile["required_evidence"])
        if has_evidence:
            gap_description = None
            action_required = None
        else:
            gap_description = (
                f"Task appears to be subject to {framework} ({profile['description']}) "
                f"but lacks required compliance evidence or documentation."
            )
            action_required = (
                f"Before development: document {framework} compliance approach, "
                f"attach evidence, and obtain required sign-off."
            )
        results.append(ComplianceResult(
            framework=framework,
            description=profile["description"],
            triggered=True,
            has_evidence=has_evidence,
            gap_description=gap_description,
            action_required=action_required,
        ))

    return results


def has_compliance_gaps(task: dict) -> bool:
    return any(r.triggered and not r.has_evidence for r in check_compliance(task))
