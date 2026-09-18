# PET — Personal Engineering Toolkit

> **Repository analysis infrastructure for engineering teams.**

PET is an independent systems project for turning a software repository into **bounded, deterministic, explainable engineering signals**. The goal is not to make an LLM sound intelligent; it is to establish a trustworthy analysis layer that downstream retrieval or model reasoning can consume.

## The engineering problem

Repository context is fragmented across source files, tests, documentation, configuration, and structure. Naive AI analysis creates two problems: it can consume too much untrusted input, and it can produce conclusions that are difficult to verify.

PET attacks the first layer directly: **safe ingestion → deterministic signals → evidence-backed findings**.

```text
Repository
    │
    ▼
Bounded + security-aware traversal
    │
    ▼
File / language / test / documentation signals
    │
    ▼
Deterministic engineering model
    │
    ▼
Findings + source evidence
    │
    └──────► optional AI / retrieval layer
```

## What is actually implemented

- Deterministic repository inventory across source files, languages, tests, documentation, and maintainability signals.
- Security-aware scanning with bounded reads, binary/invalid-content rejection, sensitive-file exclusion, and symlink-safe traversal.
- Typed FastAPI request/response contracts for repository analysis.
- Next.js + React interface for presenting engineering findings.
- Provider isolation so model access does not sit on the critical deterministic analysis path.
- Explainable engineering-health signals derived from repository artifacts rather than model-generated claims.

## Supported file classification

PET classifies common application, interface, query, configuration, documentation, and container artifacts by extension or filename. Current classifications include:

- **Application/source:** Python, TypeScript, JavaScript, Vue, Svelte, HTML, CSS, Java, Go, Rust, C, C++, C#, Shell (`.sh`, `.bash`, `.zsh`, `.fish`), Kotlin (`.kt`, `.kts`), Swift, SQL, and GraphQL (`.graphql`, `.gql`).
- **Documentation/configuration:** Markdown, JSON, YAML, and TOML (`.toml`).
- **Container tooling:** `Dockerfile` and `Dockerfile.*` variants are recognized by filename and count as source artifacts for source/maintainability signals.

Unknown text files remain analyzable and are reported as `Other`; binary, invalid UTF-8, oversized, sensitive, or symlinked files are excluded before classification.

## Safety boundary

The analyzer enforces limits **before analysis**:

- Maximum **1 MB per candidate file**.
- Maximum **10,000 valid text files** per scan.
- Invalid UTF-8, NUL-containing, binary, oversized, and symlinked files are skipped.
- Common generated/dependency directories are excluded.
- Credential/key artifacts and known sensitive configuration paths are excluded, including `.envrc` files.
- When `PET_REPOSITORY_ROOT` is configured, requested paths must remain inside that operator-defined root.

These are implementation constraints, not README-only promises. The analyzer keeps bounded text and metadata rather than loading entire repositories into memory.

### Scan truncation semantics

`max_files` is a **scan limit**, not just an output limit. When the analyzer reaches the configured limit, it stops traversing and reports an `analysis` risk indicating that the scan was truncated. The API accepts values from **1 to 10,000**; the default is **2,500**.

The result also caps detailed per-file `signals` at **100**. If more files were analyzed than can be represented in that list, the result includes a low-severity `analysis` risk describing the number of analyzed signals and returned signals. Aggregate file/language/test/documentation metrics still represent the full bounded scan result.

## Engineering decisions

| Decision | Reason |
|---|---|
| Deterministic first | Creates a reproducible source of truth before AI reasoning. |
| Evidence stays attached | Findings can be inspected instead of trusted blindly. |
| Explicit resource bounds | Prevents pathological repository scans. |
| Sensitive-path filtering | Reduces the chance of ingesting credential material. |
| Symlink rejection | Prevents traversal outside the intended tree. |
| Provider isolation | Keeps the core path testable without API credentials. |

## Quick start