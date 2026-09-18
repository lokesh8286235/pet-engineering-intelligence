from __future__ import annotations

import os
from pathlib import Path

from .models import AnalysisResult, FileSignal, Risk

IGNORED = {".git", ".next", ".turbo", ".vercel", ".cache", ".parcel-cache", "node_modules", ".terraform", ".gradle", "dist", "build", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", "coverage", "htmlcov", ".ds_store", "thumbs.db"}
SENSITIVE_FILENAMES = {
    ".env", ".envrc", ".netrc", ".npmrc", ".pypirc", ".git-credentials", "credentials.json", "credentials.yml", "credentials.yaml",
    "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa",
}
SENSITIVE_RELATIVE_PATHS = {
    (".aws", "credentials"),
    (".docker", "config.json"),
    (".config", "gcloud", "application_default_credentials.json"),
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 10_000
MAX_SIGNALS = 100
EXTENSIONS = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".vue": "Vue", ".svelte": "Svelte", ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "CSS", ".sass": "CSS",
    ".java": "Java", ".go": "Go", ".rs": "Rust",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".fish": "Shell",
    ".sql": "SQL", ".graphql": "GraphQL", ".gql": "GraphQL", ".md": "Markdown", ".mdx": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
}
SPECIAL_FILENAMES = {"dockerfile": "Dockerfile"}
SOURCE_KINDS = {"Python", "TypeScript", "JavaScript", "Vue", "Svelte", "HTML", "CSS", "Java", "Go", "Rust", "Shell", "SQL", "GraphQL", "Dockerfile"}


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    relative_parts = tuple(part.lower() for part in path.parts)
    return (
        name in SENSITIVE_FILENAMES
        or any(relative_parts[-len(candidate):] == candidate for candidate in SENSITIVE_RELATIVE_PATHS)
        or name.startswith(".env.")
        or path.suffix.lower() in SENSITIVE_SUFFIXES
    )


def _is_test_file(path: Path) -> bool:
    """Return True for conventional test/spec files without substring false positives."""
    parts = [part.lower() for part in path.parts]
    original_stem = path.stem
    stem = original_stem.lower()
    return (
        any(part in {"test", "tests", "__tests__", "spec", "specs"} for part in parts)
        or stem in {"test", "spec"}
        or stem.startswith("test_")
        or stem.endswith("_test")
        or stem.startswith("spec_")
        or stem.endswith("_spec")
        or stem.endswith(".test")
        or stem.endswith(".spec")
        or (original_stem.startswith("Test") and len(original_stem) > 4 and original_stem[4].isupper())
    )


def _read_text(path: Path) -> str | None:
    """Read a bounded UTF-8 text file, protecting against growth and binary data."""
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_FILE_BYTES + 1)
    except OSError:
        return None
    if len(data) > MAX_FILE_BYTES or b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _files(root: Path, limit: int) -> tuple[list[tuple[Path, int, int, bool]], bool]:
    """Collect only metadata needed by analysis so scans don't retain file contents."""
    found: list[tuple[Path, int, int, bool]] = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(
            d for d in dirs
            if d.lower() not in IGNORED and not (Path(current) / d).is_symlink()
        )
        for name in sorted(names):
            path = Path(current) / name
            if path.is_symlink() or not path.is_file() or _is_sensitive(path):
                continue
            text = _read_text(path)
            if text is None:
                continue
            size_bytes = len(text.encode("utf-8"))
            found.append((path, size_bytes, len(text.splitlines()), not text.strip()))
            if len(found) > limit:
                return found[:limit], True
    return found, False


def _kind_for_path(path: Path) -> str:
    name = path.name.lower()
    if name == "dockerfile" or name.startswith("dockerfile."):
        return "Dockerfile"
    return EXTENSIONS.get(path.suffix.lower(), "Other")


def analyze_repository(raw_path: str, max_files: int = 2500) -> AnalysisResult:
    root = Path(raw_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("path must point to an existing directory")
    if type(max_files) is not int or not 1 <= max_files <= MAX_FILES:
        raise ValueError(f"max_files must be between 1 and {MAX_FILES}")

    signals: list[FileSignal] = []
    languages: dict[str, int] = {}
    total_lines = 0
    source_files = 0
    test_files = 0
    docs = 0
    large_files: list[str] = []
    empty_source_files: list[str] = []

    files, truncated = _files(root, max_files)
    for path, size_bytes, lines, is_empty in files:
        rel = str(path.relative_to(root))
        kind = _kind_for_path(path)
        languages[kind] = languages.get(kind, 0) + 1
        total_lines += lines
        if kind in SOURCE_KINDS:
            source_files += 1
        if _is_test_file(path.relative_to(root)):
            test_files += 1
        if kind == "Markdown":
            docs += 1
        if kind in SOURCE_KINDS and lines > 800:
            large_files.append(rel)
        if kind in SOURCE_KINDS and is_empty:
            empty_source_files.append(rel)
        signals.append(FileSignal(path=rel, kind=kind, size_bytes=size_bytes, lines=lines))

    risks: list[Risk] = []
    file_count = len(signals)
    if file_count == 0:
        risks.append(Risk(severity="high", category="analysis", message="No analyzable files detected", evidence=["files=0"]))
    elif source_files == 0:
        risks.append(Risk(severity="medium", category="analysis", message="No source-code files detected", evidence=["source_files=0"]))
    if file_count and test_files == 0:
        risks.append(Risk(severity="high", category="testing", message="No test/spec files detected", evidence=["test_files=0"]))
    if file_count and docs == 0:
        risks.append(Risk(severity="medium", category="documentation", message="No Markdown documentation detected", evidence=["markdown_files=0"]))
    if large_files:
        risks.append(Risk(severity="medium", category="maintainability", message=f"{len(large_files)} large source files exceed 800 lines", evidence=large_files[:8]))
    if empty_source_files:
        risks.append(Risk(severity="low", category="maintainability", message=f"{len(empty_source_files)} empty source files detected", evidence=empty_source_files[:8]))
    if truncated:
        risks.append(Risk(severity="low", category="analysis", message="Analysis scan truncated at configured file limit", evidence=[f"max_files={max_files}"]))
    if file_count > MAX_SIGNALS:
        risks.append(Risk(
            severity="low",
            category="analysis",
            message="Detailed file signals truncated in the result",
            evidence=[f"signals={file_count}", f"returned_signals={MAX_SIGNALS}"],
        ))

    score = 0 if file_count == 0 else 100
    score -= 20 if source_files == 0 and file_count else 0
    score -= 25 if test_files == 0 and file_count else 0
    score -= 10 if docs == 0 and file_count else 0
    score -= min(20, len(large_files) * 2)
    score -= min(10, len(empty_source_files))
    score -= 10 if truncated else 0
    score = max(0, min(100, score))

    return AnalysisResult(
        repository=root.name,
        files=file_count,
        source_files=source_files,
        lines=total_lines,
        languages=dict(sorted(languages.items(), key=lambda item: item[1], reverse=True)),
        signals=signals[:MAX_SIGNALS],
        risks=risks,
        health_score=score,
    )
