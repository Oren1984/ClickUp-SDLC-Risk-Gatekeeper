# Static Portfolio Site

**SDLC Risk & Compliance Gatekeeper**
Oren Salami | Technology Project Management + AI Tools

---

## What is this?

This is a standalone static portfolio page for the SDLC Risk & Compliance Gatekeeper project.
It explains the project, the problem it solves, the core review flows, the architecture,
and how to run the Streamlit demo — in a clean, recruiter-ready format.

It is separate from the Streamlit application and has no backend or external services.

---

## How to run locally

**Option 1 — Python HTTP server (recommended):**

```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

**Option 2 — Open directly in a browser:**

Double-click `index.html` or drag it into any browser window.
The page works without a server — no build step, no npm, no dependencies.

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main portfolio page — all content |
| `styles.css` | All styling — responsive, self-contained, no CDN |
| `README.md` | This file |

---

## What it covers

- Project title and brand positioning
- Problem statement — why tasks fail before development
- Solution overview — risk score, gate decision, findings, recommendations
- Core review flows — QA, Security, Architecture, Compliance, SDLC
- Risk rules table (10 rules, weights, categories)
- Gate decisions table
- Architecture diagram — adapter-based data flow
- Dashboard capabilities
- Demo data scenarios (20 mock tasks)
- Future integration path (ClickUp, Jira, Monday, Linear, Azure DevOps, Notion)
- Run commands (Streamlit, Docker, tests)
- Project category positioning

---

## Design notes

- Self-contained: no CDN, no framework, no npm
- Uses system font stack — works on all platforms
- Responsive layout — works on desktop and mobile
- No JavaScript required for any content

---

## This site vs. the Streamlit app

| | Static Site | Streamlit App |
|-|-------------|---------------|
| Purpose | Portfolio / recruiter / course presentation | Live interactive risk review demo |
| Requires Python | No (browser only) | Yes |
| Shows live data | No | Yes |
| Needs install | No | `pip install -r requirements.txt` |
| Port | 8000 | 8501 |
