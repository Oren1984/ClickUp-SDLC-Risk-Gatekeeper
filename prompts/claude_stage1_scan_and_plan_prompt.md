# Stage 1 Prompt for Claude — Scan and Plan Only

Use this as the first working prompt after attaching:

1. `00_pipeline_controller.md`
2. `01_scan_and_plan.md`
3. `rag_retrieval_evaluation_lab_specification.md`

---

You are working on the repository:

```text
rag-retrieval-evaluation-lab
```

Project type:

```text
RAG
```

Attached specification file:

```text
rag_retrieval_evaluation_lab_specification.md
```

Your task now is ONLY to scan, analyze, and plan.

Do NOT implement.
Do NOT modify files.
Do NOT delete files.
Do NOT rename files.
Do NOT create files.
Do NOT rewrite documentation.

Read the controller, read the scan-and-plan prompt, read the specification, then scan the repository and produce the required repository audit report.

Important boundaries:

- This is a local-first RAG retrieval evaluation lab.
- It must remain RAG-only.
- Do not add Agents, MCP, CrewAI, Kubernetes, Terraform, React, or unrelated platform features.
- Streamlit is the only UI for v1.
- Mock mode is mandatory.
- ChromaDB and FAISS must be supported through modular interfaces.
- OpenAI and Gemini are optional embedding providers and must not be required for default execution.
- Docker support is required.
- Basic security, observability, and testing are required.
- Work strictly phase-by-phase.

Expected final output:

- Repository Audit Report
- Specification Summary
- Gap Analysis
- Keep / Update / Remove / Create / Unclear classification
- Staged Execution Plan
- Risks / Boundaries / Assumptions
- Confidence Summary
- Final Recommendation

Final line must be:

```text
READY FOR EXECUTION APPROVAL
```
