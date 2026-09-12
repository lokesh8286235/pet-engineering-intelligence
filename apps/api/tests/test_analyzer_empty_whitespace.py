from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_flags_whitespace_only_source_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("  \n\n\t", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.source_files == 1
    assert result.lines == 3
    risk = next(r for r in result.risks if r.category == "maintainability")
    assert risk.message == "1 empty source files detected"
    assert risk.evidence == ["app.py"]
