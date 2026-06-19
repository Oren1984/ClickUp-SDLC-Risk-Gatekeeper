# Static Portfolio Site

This folder contains a standalone static presentation page for the
ClickUp SDLC Risk Gatekeeper project.

It is designed for portfolio, recruiter, and course presentation use,
and is intentionally separate from the Streamlit demo app.

## What this static site is

- A concise project overview page (problem, solution, flows, architecture, run steps).
- A no-backend, no-build, no-dependency static site.
- A local presentation artifact for the project story.

## How to run locally

```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

You can also open index.html directly in a browser.

## Separation from Streamlit

- Static site: presentation only.
- Streamlit app: interactive SDLC risk dashboard.

## Technical constraints

- No backend.
- No external services.
- No API calls.
- No secrets.
