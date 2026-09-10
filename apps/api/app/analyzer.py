from __future__ import annotations

import os
from pathlib import Path
from collections.abc import Iterator

from .models import AnalysisResult, FileSignal, Risk

IGNORED = {".git", ".next", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
SENSITIVE_FILENAMES = {"credentials.json", "credentials.yml", "credentials.yaml"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
MAX_FILE_BYTES = 1_000_000
BINARY_SAMPLE_BYTES = 8192
MAX_FILES = 10_000
EXTENSIONS = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".java": "Java", ".go": "Go", ".rs": "Rust",
    ".sql": "SQL", ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
}


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    return (
        name in SENSITIVE_FILENAMES
        or name == ".env"
        or name.startswith(".env.")
        or path.suffix.lower() in SENSITIVE_SUFFIXES
    )


def _is_test_file(path: Path) -> bool:
    """Return True for conventional test/spec files without substring false positives."""
    parts = [part.lower() for part in path.parts]
    stem = path.stem.lower()
    return (
        any(part in {"test", "tests", "spec", "specs"} for part in parts)
        or stem in {"test", "spec"}
        or stem.startswith("test_")
        or stem.endswith("_test")
        or stem.startswith("spec_")
        or stem.endswith("_spec")
    )


def _looks_binary(path: Path) -> bool:
    """Return True when the first sample contains a NUL byte."""
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(BINARY_SAMPLE_BYTES)
    except OSError:
        return True


def _read_text(path: Path) -> str | None:
    """Read a bounded UTF-8 text file, protecting against growth and binary data."""
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_FILE_BYTES + 1)
    except OSError:
        return None
    if len(data) > MAX_FILE_BYTES:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _files(root: Path, limit: int) -> Iterator[tuple[Path, int]]:
    count = 0
    # Walk lazily so max_files can stop traversal early, while sorting each
    # directory keeps scan limits and returned signals deterministic.
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(
            d for d in dirs
            if d not in IGNORED and not (Path(current) / d).is_symlink()
        )
        for name in sorted(names):
            if count >= limit:
                return
            path = Path(current) / name
            if not path.is_file() or path.is_symlink():
                continue
            if _is_sensitive(path):
                continue
            try:
                size_bytes = path.stat().st_size
            except OSError:
                continue
            if size_bytes > MAX_FILE_BYTES:
                continue
            if _looks_binary(path):
                continue
            count += 1
            yield path, size_bytes


def analyze_repository(raw_path: str, max_files: int = 2500) -> AnalysisResult:
    root = Path(raw_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("path must point to an existing directory")
    if not 1 <= max_files <= MAX_FILES:
        raise ValueError(f"max_files must be between 1 and {MAX_FILES}")

    signals: list[FileSignal] = []
    languages: dict[str, int] = {}
    total_lines = 0
    test_files = 0
    docs = 0
    large_files: list[str] = []

    for path, size_bytes in _files(root, max_files):
        text = _read_text(path)
        if text is None:
            continue
        # splitlines() handles LF, CRLF, and legacy CR line endings without
        # counting a trailing newline as an additional source line.
        lines = len(text.splitlines())
        rel = str(path.relative_to(root))
        suffix = path.suffix.lower()
        kind = EXTENSIONS.get(suffix, "Other")
        languages[kind] = languages.get(kind, 0) + 1
        total_lines += lines
        if _is_test_file(path.relative_to(root)):
            test_files += 1
        if suffix == ".md":
            docs += 1
        if lines > 800:
            large_files.append(rel)
        signals.append(FileSignal(path=rel, kind=kind, size_bytes=size_bytes, lines=lines))

    risks: list[Risk] = []
    file_count = len(signals)
    if file_count and test_files == 0:
        risks.append(Risk(severity="high", category="testing", message="No test/spec files detected", evidence=["test_files=0"]))
    if file_count and docs == 0:
        risks.append(Risk(severity="medium", category="documentation", message="No Markdown documentation detected", evidence=["markdown_files=0"]))
    if large_files:
        risks.append(Risk(severity="medium", category="maintainability", message=f"{len(large_files)} large source files exceed 800 lines", evidence=large_files[:8]))
    if file_count >= max_files:
        risks.append(Risk(severity="low", category="analysis", message="File scan reached configured limit", evidence=[f"max_files={max_files}"]))

    score = 100
    score -= 25 if test_files == 0 and file_count else 0
    score -= 10 if docs == 0 and file_count else 0
    score -= min(20, len(large_files) * 2)
    score = max(0, min(100, score))

    return AnalysisResult(
        repository=root.name,
        files=file_count,
        lines=total_lines,
        languages=dict(sorted(languages.items(), key=lambda item: item[1], reverse=True)),
        signals=signals[:100],
        risks=risks,
        health_score=score,
    )
