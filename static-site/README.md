# Static Site — RAG Engineering Lab

**Oren Salami | 🧠 AI Systems Engineer**  
Intelligent Systems • AI Agents • Data & Automation

---

## Overview

This folder contains a **standalone static portfolio page** for the RAG Engineering Lab project. It is built with plain HTML, CSS, and vanilla JavaScript — no framework, no build step, no dependencies.

This is not the Streamlit application. It is not the RAG backend. It is a visual presentation layer designed to introduce the project to technical reviewers and recruiters.

---

## Purpose

The page presents the following aspects of the project:

- **Project overview** — what the system does and why it exists
- **Architecture** — the five-layer pipeline from document to ranked results
- **Core capabilities** — chunking strategies, embedding providers, vector stores, and UI tabs
- **Evaluation metrics** — Recall@K, Precision@K, MRR, and nDCG@K
- **Security and observability** — local-first design, environment-variable secrets, METRICS singleton
- **Testing and reliability** — stage-gated smoke tests and edge-case coverage
- **Tech stack** — grouped by category (language, vector stores, providers, UI, testing)
- **Project boundaries** — what the project is and is not

---

## Folder Structure

```
static-site/
├── index.html      # All 11 sections, semantic HTML
├── styles.css      # Dark theme, glassmorphism cards, responsive grid, animations
├── app.js          # Sticky nav, scroll reveal, counter animation, smooth scroll
└── assets/         # Reserved for future static assets (currently unused)
```

---

## How to Run Locally

From the repository root:

```bash
cd static-site
python -m http.server 8000
```

Then open your browser at:

```
http://localhost:8000
```

If port 8000 is in use, specify any free port:

```bash
python -m http.server 9000
```

No installation required. The site loads immediately from the local filesystem.

---

## What This Site Is

- A **standalone static portfolio page** for the RAG Engineering Lab
- A **visual presentation layer** — suitable for sharing with technical reviewers
- Deployable to any **static hosting service** or plain web server by uploading the folder as-is
- **No build step required** — open `index.html` directly or serve it with any HTTP server

---

## What This Site Is Not

- **Not the Streamlit application** — run `streamlit run app/streamlit_app.py` for the interactive UI
- **Not the RAG pipeline** — the retrieval and evaluation logic lives in `src/`
- **Not a backend service** — there is no server, no API, and no database behind this page
- **Not an agent system** — this project does not use LLM agents, autonomous loops, or tool-calling
- **Not an MCP or CrewAI project** — no multi-agent framework is used
- **Not a SaaS product** — the system is local-first and designed for offline use

---

## Design Notes

The page uses a hand-crafted dark theme with no external CSS framework:

- **Dark navy base** (`#0a0e1a`) with indigo/cyan accent gradient
- **Glassmorphism cards** — `backdrop-filter: blur` with semi-transparent borders
- **Sticky navigation** with blur backdrop and active-section tracking
- **Responsive layout** using CSS Grid (`auto-fit / minmax`)
- **Scroll reveal animations** via `IntersectionObserver` (no scroll event listeners)
- **Counter animations** on the metric cards, triggered on first visibility
- **Architecture diagram** built entirely from HTML and CSS — no images or SVG charts
- **Inline SVG icons** for GitHub marks; Unicode symbols for all other icons
- **Vanilla JS only** — no jQuery, no React, no bundler

---

## Deployment Notes

To deploy, upload the contents of `static-site/` to any static hosting provider or web server:

```
static-site/
├── index.html
├── styles.css
├── app.js
└── assets/
```

**Compatible with:** GitHub Pages, Netlify, Vercel (static), Amazon S3 static hosting,
any Nginx / Apache server configured to serve static files.

No `npm install`, no build command, and no framework configuration is required.

---

## Related Links

- **Project repository:** https://github.com/Oren1984/rag-retrieval-evaluation-lab
- **GitHub profile:** https://github.com/Oren1984

---

## Maintenance Notes

- **Update this site** when the core project changes significantly — for example, when a new embedding provider, vector store, or major feature is added.
- **Do not mirror every small backend change** — minor refactors, dependency bumps, and test additions do not require a site update.
- **Keep claims aligned with the actual repository state.** If a section of the site says the system supports a feature, that feature should exist in `src/` or `app/`.
- **Do not add claims about Agents, MCP, CrewAI, Kubernetes, or Terraform** unless those components are genuinely added to the project at a later date.
