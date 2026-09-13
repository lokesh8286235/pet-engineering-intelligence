# PET — Personal Engineering Toolkit

> **AI-native engineering intelligence for understanding software systems and turning evidence into decisions.**

PET is an independent engineering project exploring how AI can help engineers inspect codebases, investigate failures, prioritize engineering risk, and make better changes without hiding the evidence behind an opaque model response.

## Why this exists

Engineering context is fragmented across source code, tests, documentation, repository structure, and operational signals. PET builds a transparent analysis layer first, then leaves room for retrieval and model-assisted reasoning on top.

```text
Repository / Tests / Docs / Operational Signals
                    │
                    ▼
             Bounded ingestion
                    │
                    ▼
             Signal extraction
                    │
                    ▼
          ┌───────────────────┐
          │ Deterministic     │
          │ engineering model │
          └─────────┬─────────┘
                    │
             evidence + risks
                    │
          ┌─────────▼─────────┐
          │ Optional context  │
          │ / AI layer        │
          └─────────┬─────────┘
                    ▼
             Decision + evidence
```

## What is implemented

- **Repository intelligence** — deterministic inventory of source files, languages, tests, documentation, and maintainability signals.
- **Security-aware scanning** — bounded reads, invalid/binary content rejection, sensitive-file exclusion, and symlink-safe traversal.
- **API surface** — typed FastAPI request/response models for repository analysis.
- **Web architecture** — Next.js + React frontend for presenting engineering intelligence.
- **Provider isolation** — model access is separated from the deterministic analysis path.
- **Engineering health signals** — findings are explainable and derived from repository artifacts rather than invented by a model.

## Engineering decisions

| Decision | Why |
|---|---|
| Analyze deterministically first | Reproducibility and debuggability matter before model reasoning. |
| Bound file size and count | Prevent pathological scans and resource exhaustion. |
| Reject symlink traversal | Avoid escaping the intended repository tree. |
| Exclude credential artifacts | Do not ingest common secrets into analysis context. |
| Keep source evidence visible | Engineers need to verify why a finding exists. |
| Isolate providers | The core system remains testable without an API key. |

## Safety boundary

The repository analyzer intentionally applies multiple limits before analysis:

- Maximum **1 MB per candidate file**.
- Maximum **10,000 valid text files** per scan.
- Invalid UTF-8, NUL-containing, binary, oversized, and symlinked files are skipped.
- Common generated/dependency directories are excluded.
- Credential/key artifacts and known sensitive configuration paths are excluded.
- When `PET_REPOSITORY_ROOT` is configured, API requests must resolve inside that operator-defined root.

These controls are part of the product architecture, not just documentation. The implementation keeps bounded text and metadata rather than retaining entire repositories in memory.

## Stack

**Frontend:** Next.js · React · TypeScript  
**Backend:** Python · FastAPI · Pydantic  
**Data / AI direction:** PostgreSQL · pgvector · RAG · evaluation  
**Platform:** Docker · GitHub Actions · AWS/Kubernetes-ready architecture

## Quick start

### API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Web

```bash
cd apps/web
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## API

`POST /v1/analyze`

```json
{
  "path": "/workspace/example",
  "max_files": 2500
}
```

`GET /health` provides a lightweight service check.

## Evaluation mindset

PET is developed around a simple loop:

```text
Hypothesis → implementation → adversarial test → evidence → iterate
```

A repository-intelligence system should not receive credit merely for producing plausible prose. Findings need deterministic inputs, explicit rules, and tests for failure modes.

## Roadmap

- [x] Bounded repository analyzer
- [x] Test/documentation/maintainability signals
- [x] Sensitive-file and symlink protections
- [x] FastAPI service and frontend foundation
- [ ] Symbol and dependency graph extraction
- [ ] Hybrid lexical + vector retrieval
- [ ] Repository-aware investigation workflows
- [ ] PR risk and change-impact analysis
- [ ] OpenTelemetry instrumentation
- [ ] Versioned evaluation datasets and quality gates
- [ ] Production deployment hardening

## Status

**Active independent build.** The current focus is making repository analysis more structurally aware, measurable, and useful before adding heavier agentic behavior.

## License

MIT
