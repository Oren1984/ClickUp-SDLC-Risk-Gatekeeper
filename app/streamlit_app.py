"""ClickUp SDLC Risk Gatekeeper — Streamlit Dashboard"""
from __future__ import annotations
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

st.set_page_config(
    page_title="ClickUp SDLC Risk Gatekeeper",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🛡️",
)

from src.core.clickup_adapter import load_tasks
from src.core.risk_reviewer import RiskReviewer
from src.core.compliance_checks import check_compliance
from src.core.report_generator import generate_task_report, generate_summary_report


# ── Constants ─────────────────────────────────────────────────────────────

RISK_COLORS = {
    "Low":      "#28a745",
    "Medium":   "#ffc107",
    "High":     "#fd7e14",
    "Critical": "#dc3545",
}

GATE_ICONS = {
    "Approved for Development":    "✅",
    "Needs Clarification":         "💬",
    "Requires QA Review":          "🧪",
    "Requires Security Review":    "🔒",
    "Requires Architecture Review":"🏗️",
    "Blocked":                     "🚫",
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
RISK_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


# ── Load and review data ───────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_and_review():
    tasks = load_tasks()
    reviewer = RiskReviewer()
    reports = []
    for task in tasks:
        result = reviewer.review(task)
        report = generate_task_report(task, result)
        report["task_obj"] = task
        reports.append(report)
    summary = generate_summary_report(reports)
    return tasks, reports, summary


tasks, reports, summary = load_and_review()


# ── Header ────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div style="padding:0.6rem 0 0.4rem; border-bottom:2px solid #e0e6ed; margin-bottom:0.8rem;">
        <h1 style="margin:0; font-size:1.8rem; line-height:1.25;">
            🛡️ ClickUp SDLC Risk Gatekeeper
        </h1>
        <p style="margin:0.25rem 0 0; font-size:0.95rem; color:#444;">
            <strong>Oren Salami</strong> | Technology Project Management + AI Tools
        </p>
        <p style="margin:0.1rem 0 0; color:#888; font-size:0.82rem;">
            AI-assisted SDLC risk &amp; compliance review for ClickUp-style software delivery workflows
            &nbsp;&mdash;&nbsp; <strong>Demo mode</strong>: all data is local mock JSON, no credentials required
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Summary Metrics ────────────────────────────────────────────────────────

st.subheader("Project Risk Overview")
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
m1.metric("Total Tasks",           summary["total_tasks"])
m2.metric("✅ Approved",           summary["approved_for_development"])
m3.metric("🚫 Blocked",            summary["blocked"],            delta=None)
m4.metric("🔴 High / Critical",    summary["high_risk_or_critical"])
m5.metric("🧪 Needs QA",           summary["requires_qa_review"])
m6.metric("🔒 Needs Security",     summary["requires_security_review"])
m7.metric("🏗️ Needs Arch Review",  summary["requires_architecture_review"])


# ── Sidebar filters ────────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔍 Filters")

    all_sprints = sorted({r["sprint"] for r in reports})
    selected_sprints = st.multiselect("Sprint", all_sprints, default=all_sprints)

    all_statuses = sorted({r["status"] for r in reports})
    selected_statuses = st.multiselect("Status", all_statuses, default=all_statuses)

    all_risk_levels = ["Critical", "High", "Medium", "Low"]
    selected_risk = st.multiselect("Risk Level", all_risk_levels, default=all_risk_levels)

    all_gates = list(GATE_ICONS.keys())
    selected_gates = st.multiselect("Gate Decision", all_gates, default=all_gates)

    st.divider()
    st.caption("Demo mode — all data is local mock JSON. No API keys or credentials required.")
    st.caption("`src/integrations/clickup_api_client.py` implements read-only fetch methods (Phase 1) — not used by this dashboard. Write-back is not implemented (Phase 2). See `docs/future_clickup_integration.md`.")


# ── Filter reports ────────────────────────────────────────────────────────

filtered = [
    r for r in reports
    if r["sprint"] in selected_sprints
    and r["status"] in selected_statuses
    and r["risk_level"] in selected_risk
    and r["gate_decision"] in selected_gates
]
filtered.sort(key=lambda r: (RISK_ORDER.get(r["risk_level"], 9), PRIORITY_ORDER.get(r["task_obj"].get("priority",""), 9)))


# ── Tabs ──────────────────────────────────────────────────────────────────

tab_dashboard, tab_detail, tab_compliance, tab_about = st.tabs(
    ["📋 Task Risk Dashboard", "🔎 Task Detail", "⚖️ Compliance View", "ℹ️ About This Project"]
)


# ─────────────────────────────────────────────────────────────────────────
# Tab 1 — Task Risk Dashboard
# ─────────────────────────────────────────────────────────────────────────

with tab_dashboard:
    if not filtered:
        st.info("No tasks match the current filters.")
    else:
        st.caption(f"Showing {len(filtered)} of {len(reports)} tasks — sorted by risk level, then priority.")
        for r in filtered:
            task = r["task_obj"]
            risk_color = RISK_COLORS.get(r["risk_level"], "#6c757d")
            gate_icon = GATE_ICONS.get(r["gate_decision"], "❓")
            priority = task.get("priority", "").upper()

            with st.expander(
                f"{gate_icon} **{r['task_id']}** — {r['title']}  |  "
                f"Risk: {r['risk_level']} ({r['risk_score']}/100)  |  {r['gate_decision']}",
                expanded=False,
            ):
                col1, col2, col3, col4 = st.columns(4)
                col1.markdown(f"**Sprint:** {r['sprint']}")
                col2.markdown(f"**Status:** {r['status']}")
                col3.markdown(f"**Priority:** `{priority}`")
                col4.markdown(f"**Assignee:** {r['assignee']}")

                st.markdown(
                    f"<div style='display:inline-block; padding:4px 12px; border-radius:4px; "
                    f"background:{risk_color}; color:white; font-weight:bold; margin:4px 0;'>"
                    f"Risk Score: {r['risk_score']}/100 — {r['risk_level']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Gate Decision:** {gate_icon} {r['gate_decision']}")

                if r["findings"]:
                    st.markdown("**Findings:**")
                    for finding in r["findings"]:
                        st.markdown(f"- ⚠️ {finding}")
                else:
                    st.success("No findings — task passes all risk rules.")

                if r["recommendations"]:
                    st.markdown("**Recommendations:**")
                    for rec in r["recommendations"]:
                        st.markdown(f"- 💡 {rec}")

                tags = task.get("tags") or []
                if tags:
                    st.markdown(f"**Tags:** {', '.join(f'`{t}`' for t in tags)}")
                deps = task.get("dependencies") or []
                if deps:
                    st.markdown(f"**Dependencies:** {', '.join(deps)}")
                if task.get("due_date"):
                    st.markdown(f"**Due Date:** {task['due_date']}")


# ─────────────────────────────────────────────────────────────────────────
# Tab 2 — Task Detail
# ─────────────────────────────────────────────────────────────────────────

with tab_detail:
    st.subheader("Task Detail View")
    task_ids = [r["task_id"] for r in reports]
    task_labels = [f"{r['task_id']} — {r['title'][:60]}" for r in reports]
    selected_label = st.selectbox("Select a task", task_labels, index=0)
    selected_idx = task_labels.index(selected_label)
    selected_report = reports[selected_idx]
    selected_task = selected_report["task_obj"]

    risk_color = RISK_COLORS.get(selected_report["risk_level"], "#6c757d")
    gate_icon = GATE_ICONS.get(selected_report["gate_decision"], "❓")

    st.markdown(f"### {selected_report['task_id']}: {selected_report['title']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sprint", selected_report["sprint"])
    c2.metric("Status", selected_report["status"])
    c3.metric("Priority", selected_task.get("priority", "").upper())
    c4.metric("Assignee", selected_report["assignee"])

    st.markdown("---")

    rc1, rc2, rc3 = st.columns(3)
    rc1.markdown(
        f"<div style='padding:8px 16px; border-radius:6px; background:{risk_color}; "
        f"color:white; font-weight:bold; text-align:center;'>"
        f"Risk Score: {selected_report['risk_score']}/100<br>{selected_report['risk_level']}</div>",
        unsafe_allow_html=True,
    )
    rc2.markdown(f"**Gate Decision:**  \n{gate_icon} {selected_report['gate_decision']}")
    rc3.markdown(f"**Rules Triggered:**  \n{', '.join(selected_report['triggered_rules']) or 'None'}")

    st.markdown("---")
    st.markdown("#### Task Description")
    st.write(selected_task.get("description") or "_No description provided._")

    st.markdown("#### Acceptance Criteria")
    ac = selected_task.get("acceptance_criteria")
    if ac:
        st.write(ac)
    else:
        st.warning("No acceptance criteria defined.")

    col_sec, col_arch, col_qa = st.columns(3)
    with col_sec:
        st.markdown("**Security Notes**")
        sn = selected_task.get("security_notes")
        if sn:
            st.info(sn)
        else:
            st.warning("None")
    with col_arch:
        st.markdown("**Architecture Notes**")
        an = selected_task.get("architecture_notes")
        if an:
            st.info(an)
        else:
            st.warning("None")
    with col_qa:
        st.markdown("**QA Notes**")
        qn = selected_task.get("qa_notes")
        if qn:
            st.info(qn)
        else:
            st.warning("None")

    st.markdown("---")
    st.markdown("#### Findings & Recommendations")
    if selected_report["findings"]:
        for i, (finding, rec) in enumerate(zip(selected_report["findings"], selected_report["recommendations"]), 1):
            st.markdown(f"**{i}. Finding:** ⚠️ {finding}")
            st.markdown(f"   **Recommendation:** 💡 {rec}")
            st.markdown("---")
    else:
        st.success("No findings. This task passes all risk checks.")

    tags = selected_task.get("tags") or []
    if tags:
        st.markdown(f"**Tags:** {', '.join(f'`{t}`' for t in tags)}")
    deps = selected_task.get("dependencies") or []
    if deps:
        st.markdown(f"**Dependencies:** {', '.join(deps)}")
    if selected_task.get("due_date"):
        st.markdown(f"**Due Date:** {selected_task['due_date']}")
    st.markdown(f"**DoD Status:** {selected_task.get('definition_of_done_status', 'unknown')}")


# ─────────────────────────────────────────────────────────────────────────
# Tab 3 — Compliance View
# ─────────────────────────────────────────────────────────────────────────

with tab_compliance:
    st.subheader("Compliance Gap Analysis")
    st.caption("Tasks flagged against GDPR, PCI-DSS, HIPAA, SOX, and general security compliance frameworks.")

    compliance_rows = []
    for r in reports:
        comp_results = check_compliance(r["task_obj"])
        for cr in comp_results:
            compliance_rows.append({
                "task_id": r["task_id"],
                "title": r["title"][:55],
                "framework": cr.framework,
                "has_evidence": cr.has_evidence,
                "gap": cr.gap_description or "Evidence found",
                "action": cr.action_required or "No action required",
            })

    if not compliance_rows:
        st.success("No compliance-flagged tasks found.")
    else:
        frameworks = sorted({row["framework"] for row in compliance_rows})
        selected_fw = st.multiselect("Filter by framework", frameworks, default=frameworks)
        show_gaps_only = st.checkbox("Show gaps only (missing evidence)", value=True)

        displayed = [
            row for row in compliance_rows
            if row["framework"] in selected_fw
            and (not show_gaps_only or not row["has_evidence"])
        ]

        if not displayed:
            st.success("No compliance gaps for selected filters.")
        else:
            for row in displayed:
                status_icon = "✅" if row["has_evidence"] else "❌"
                with st.expander(
                    f"{status_icon} {row['task_id']} — {row['title']} | {row['framework']}",
                    expanded=not row["has_evidence"],
                ):
                    st.markdown(f"**Framework:** {row['framework']}")
                    st.markdown(f"**Evidence status:** {status_icon} {'Evidence found' if row['has_evidence'] else 'MISSING'}")
                    if not row["has_evidence"]:
                        st.warning(f"**Gap:** {row['gap']}")
                        st.info(f"**Required action:** {row['action']}")


# ─────────────────────────────────────────────────────────────────────────
# Tab 4 — About
# ─────────────────────────────────────────────────────────────────────────

with tab_about:
    st.subheader("About This Project")
    st.markdown("""
**ClickUp SDLC Risk Gatekeeper** is a portfolio demonstration of an AI-assisted
governance and risk-review tool for ClickUp-style software delivery workflows.
It reviews tasks, user stories, and sprint items for delivery risk, QA readiness,
acceptance criteria quality, security and compliance gaps, and Definition of Done alignment —
before work enters development.

This is not a generic chatbot and not a ClickUp clone. It is a structured SDLC risk gate.

---

### What problem does this solve?

In Agile/Scrum engineering teams, tasks often enter development sprints with:
- Missing or vague acceptance criteria
- No QA test plan
- Security-sensitive changes without a threat model
- AI/LLM features without documented readiness signals (evaluation criteria, groundedness, cost awareness, fallback behavior, permission sensitivity, or guardrails)
- Architecture-impacting changes without a design review
- Compliance requirements (GDPR, PCI, HIPAA) without evidence

This tool acts as an **automated first-pass reviewer** that catches these gaps early,
before they become expensive bugs, security incidents, or compliance violations.

---

### How it works

1. Tasks are loaded from a ClickUp-compatible JSON structure (mock data in this demo)
2. Each task is analyzed by a deterministic rule-based risk engine (`src/core/risk_reviewer.py`)
3. 10 SDLC risk rules are applied covering: acceptance criteria, QA, security, AI task readiness, architecture, compliance, due dates, and dependencies
4. Each task receives a **risk score (0–100)**, **risk level**, **gate decision**, **findings**, and **recommendations**
5. The dashboard provides a project-wide risk overview and per-task drill-down

---

### Risk Rules

| Rule | What it checks |
|------|----------------|
| RULE-001 | Missing or insufficient acceptance criteria |
| RULE-002 | No QA notes or test plan |
| RULE-003 | Definition of Done not confirmed |
| RULE-004 | Security-sensitive task without security notes |
| RULE-005 | AI/LLM task with no documented readiness signal (evaluation criteria, groundedness, cost awareness, fallback, tool/data permission sensitivity, or guardrails) |
| RULE-006 | Architecture-impacting task without architecture notes |
| RULE-007 | Critical priority with vague scope |
| RULE-008 | Task blocked by unresolved dependency |
| RULE-009 | Compliance task without evidence |
| RULE-010 | Due date overdue or at immediate risk |

---

### What is mock data?

All 20 tasks are realistic but fictional. They use a ClickUp-style JSON schema and are
stored in `data/clickup_demo/tasks.json`. No real workspace is connected.

---

### AI Governance & Human-in-the-Loop

The gatekeeper is a **decision-support tool**, not an autonomous decision-maker.

- AI recommendations are **advisory** — PMs, QA leads, and Tech Leads make all final decisions
- Every finding is **explainable** — each rule states exactly what is missing and why it matters
- **No task is automatically blocked or approved** without human review
- See `docs/AI_GOVERNANCE_AND_RISK_PRINCIPLES.md` and `docs/HUMAN_IN_THE_LOOP_WORKFLOW.md`

### ClickUp API Integration Status

This dashboard always loads mock data through `src/core/clickup_adapter.py` — it does not
call the ClickUp API, regardless of whether `CLICKUP_API_TOKEN` is set.

- **Phase 1 (implemented, tested):** `src/integrations/clickup_api_client.py` provides
  read-only `fetch_tasks()` and `fetch_task_by_id()` methods against the ClickUp v2 API.
  They are usable directly and via `scripts/check_clickup_connection.py`, but are not
  called by this dashboard.
- **Phase 2 (not implemented):** write-back methods (`post_review_comment`, `set_risk_label`,
  `update_task_status`) raise `NotImplementedError` by design.
- `src/integrations/mock_client.py` implements the same `TaskClient` protocol as the API
  client, wrapping `clickup_adapter.py`'s local JSON loader.
- `src/integrations/base.py` defines the `TaskClient` protocol all adapters must satisfy.
- Wiring the dashboard to live data would require swapping the adapter call in
  `app/streamlit_app.py` — the risk engine stays unchanged.
- See `docs/future_clickup_integration.md` for the integration roadmap.

---

### Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Risk Engine | Python (rule-based, deterministic) |
| Data | JSON mock data (ClickUp-style schema) |
| Tests | pytest |
| Packaging | Docker, Docker Compose |

---

**Author:** Oren Salami | AI Systems Engineer
**Purpose:** Portfolio demonstration — SDLC, Agile, Risk Management, QA, Compliance
    """)
