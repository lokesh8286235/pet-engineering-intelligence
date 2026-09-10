# PET — Personal Engineering Toolkit

> **An AI-native engineering workspace for turning software signals into actionable decisions.**

**Independent Project · AI Engineering · Full-Stack · Developer Tools**

PET is an independent engineering project exploring how AI can help engineers understand code, investigate failures, prioritize technical debt, and make better changes while keeping the underlying evidence visible.

## Why PET?

Engineering signals are fragmented across source code, tests, logs, pull requests, incidents, and documentation. PET creates a transparent intelligence layer across those signals.

```text
Repository / Logs / Tests / PRs
            │
            ▼
      ┌─────────────┐
      │ Signal Layer│  normalize + fingerprint
      └──────┬──────┘
             ▼
      ┌─────────────┐
      │   Context   │  retrieve relevant evidence
      │    Engine   │
      └──────┬──────┘
             ▼
      ┌─────────────┐
      │ Intelligence│  explain / diagnose / recommend
      │    Layer    │
      └──────┬──────┘
             ▼
       Decision + Evidence
```

## Core capabilities

- **Code intelligence** — inspect repository structure, symbols, dependencies, and hotspots.
- **Failure investigation** — correlate errors with recent changes and relevant source context.
- **Engineering health** — surface maintainability, testing, documentation, and reliability signals.
- **Evidence-first answers** — keep relevant source evidence attached to conclusions.
- **Provider-neutral AI** — model access stays behind a replaceable interface.
- **Local-first development** — deterministic analysis remains useful without an external model API.

## Engineering principles

| Principle | PET approach |
|---|---|
| Evidence over confidence | Return source context with conclusions |
| Determinism where possible | Analyze before invoking AI |
| Provider neutrality | Isolate model access behind interfaces |
| Secure by default | Bound reads and avoid symlink traversal |
| Observable systems | Measure latency, errors, quality, and cost |
| Small interfaces | Separate ingestion, context, intelligence, and presentation |

## Stack

**Frontend:** Next.js · React · TypeScript  
**Backend:** Python · FastAPI · Pydantic  
**Data:** PostgreSQL · pgvector · Redis  
**AI:** RAG · tool calling · structured outputs · evaluation  
**Platform:** Docker · GitHub Actions · AWS/Kubernetes-ready architecture

## Repository layout

```text
pet-engineering-intelligence/
├── apps/
│   ├── api/              # FastAPI service
│   └── web/              # Next.js interface
├── packages/             # Shared contracts and utilities
├── evaluation/           # Retrieval and answer-quality benchmarks
├── docs/                 # Architecture decisions and API notes
├── tests/                # Unit, integration, and end-to-end tests
└── .github/workflows/    # Continuous integration
```

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

## Analyzer safety

The repository analyzer is intentionally bounded and deterministic before any AI layer is invoked:

- Reads at most **1 MB per candidate file** and rejects files that grow beyond that bound.
- Rejects NUL-containing and invalid UTF-8 files instead of silently decoding corrupted content.
- Skips sensitive credential/key files and common generated or dependency directories.
- Does not follow symbolic links during repository traversal.
- Caps a single analysis request at **10,000 valid text files**; rejected/binary files do not consume that limit.

These constraints keep scans predictable while reducing accidental ingestion of secrets, generated artifacts, or binary data.

## Quality bar

PET is being developed as a **real engineering project**, not a static portfolio demo. The target is reproducible tests, explicit architecture decisions, measurable AI quality, secure repository handling, and production-oriented deployment practices.

## Roadmap

- [x] Repository analyzer
- [ ] Symbol/dependency graph extraction
- [ ] PostgreSQL + pgvector indexing
- [ ] Hybrid retrieval + reranking
- [ ] Repository-aware agent tools
- [ ] Failure/incident investigation workflow
- [ ] Evaluation harness and regression gates
- [ ] OpenTelemetry instrumentation
- [ ] Production deployment

## Status

**Active independent build.** Architecture and implementation will evolve as capabilities are validated.

## License

MIT
