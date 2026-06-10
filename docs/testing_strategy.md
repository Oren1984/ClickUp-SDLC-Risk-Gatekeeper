# Testing Strategy

## Overview

Tests are written with pytest and cover the three core modules:
adapter loading, risk reviewer logic, and compliance checks.
All tests run offline with no API keys or external services required.

## Test Files

| File | Coverage |
|------|---------|
| `tests/test_clickup_adapter.py` | Data loading, field validation, task lookup |
| `tests/test_risk_reviewer.py` | Scoring, rule detection, gate decisions |
| `tests/test_compliance_checks.py` | Compliance framework detection and gap analysis |

## Running Tests

```bash
pytest                   # all tests
pytest -v                # verbose output
pytest --cov=src         # with coverage report
pytest tests/test_risk_reviewer.py -v  # single file
```

## Test Categories

### Adapter Tests
- Tasks load as a non-empty list
- All tasks have required fields (task_id, title, status, etc.)
- Task IDs are unique
- `get_task_by_id` works for found and not-found cases
- Policies, DoD, and guidelines load correctly

### Risk Reviewer Tests
- Score-to-level mapping (boundary values)
- Clean task returns Low risk and Approved gate
- Each individual rule triggers correctly on missing data
- Each individual rule passes correctly when data is sufficient
- Blocked task returns Blocked gate decision
- Risk score is capped at 100

### Compliance Tests
- Non-compliance task returns empty results
- GDPR keyword triggers GDPR framework check
- GDPR with evidence returns no gap
- GDPR without evidence returns gap + action
- PCI keyword triggers PCI check
- Multiple frameworks detected on multi-concern task
- `has_compliance_gaps()` returns True/False correctly

## What is Not Tested

| Not tested | Reason |
|-----------|--------|
| Streamlit UI | Requires browser; correctness validated by running the app |
| ClickUp API stubs | Raise NotImplementedError by design — no token available |
| Docker build | Covered by manual smoke test |

## Testing Philosophy

- Tests validate behavior, not implementation details
- No mocking of core modules (they are pure functions)
- No external dependencies in tests
- Fixtures use explicit task dictionaries for readability
