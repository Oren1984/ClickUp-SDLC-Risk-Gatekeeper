# SDLC Risk & Compliance Gatekeeper

**Oren Salami | Technology Project Management + AI Tools**

## Overview

SDLC Risk & Compliance Gatekeeper is a local portfolio demo that adds an early
SDLC risk and compliance gate to a ClickUp-style task workflow.

The system reviews tasks before development and flags gaps in requirements,
QA readiness, security, architecture, and compliance.

## ClickUp-Style Demo Workflow Note

This repository uses local ClickUp-style mock JSON data.
No external APIs, no secrets, and no cloud setup are required.

The adapter pattern is in place so a real project-management API can be connected later.

## How to Run Streamlit

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Open: http://localhost:8501

## Static Portfolio Site

The static presentation site is in [static-site](static-site).
It is separate from the Streamlit app and intended for portfolio/recruiter/course presentation.

```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

## Run Tests

```bash
pytest
```

## Documentation

- [docs/project_overview.md](docs/project_overview.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/workflow.md](docs/workflow.md)
- [docs/demo_scenarios.md](docs/demo_scenarios.md)
- [docs/future_clickup_integration.md](docs/future_clickup_integration.md)
- [docs/testing_strategy.md](docs/testing_strategy.md)
- [docs/limitations.md](docs/limitations.md)

## Project Category

**Technology Project Management + AI Tools**

## License

MIT License. See [LICENSE](LICENSE).
