from __future__ import annotations

from pathlib import Path

from .models import AnalysisResult, FileSignal, Risk

IGNORED = {".git", ".next", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
SENSITIVE_FILENAMES = {"credentials.json", "credentials.yml", "credentials.yaml"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
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


def _files(root: Path, limit: int):
    count = 0
    for path in root.rglob("*"):
        if count >= limit:
            break
        if not path.is_file() or any(part in IGNORED for part in path.parts):
            continue
        if _is_sensitive(path):
            continue
        try:
            if path.is_symlink() or path.stat().st_size > 1_000_000:
                continue
        except OSError:
            continue
        count += 1
        yield path


def analyze_repository(raw_path: str, max_files: int = 2500) -> AnalysisResult:
    root = Path(raw_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("path must point to an existing directory")
    if max_files <= 0:
        raise ValueError("max_files must be greater than zero")

    signals: list[FileSignal] = []
    languages: dict[str, int] = {}
    total_lines = 0
    test_files = 0
    docs = 0
    large_files: list[str] = []

    for path in _files(root, max_files):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            size_bytes = path.stat().st_size
        except OSError:
            continue
        # UTF-8 decoding can silently turn arbitrary binary data into text.
        # Treat NUL-containing files as binary so they don't pollute code metrics.
        if "\x00" in text:
            continue
        lines = text.count("\n") + (1 if text else 0)
        rel = str(path.relative_to(root))
        suffix = path.suffix.lower()
        kind = EXTENSIONS.get(suffix, "Other")
        languages[kind] = languages.get(kind, 0) + 1
        total_lines += lines
        lower = rel.lower()
        if "test" in lower or "spec" in lower:
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
