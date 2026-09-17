from pathlib import Path

from app.analyzer import analyze_repository


def test_whitespace_only_source_is_reported_as_empty(tmp_path: Path):
    (tmp_path / "placeholder.py").write_text("  \n\t\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.source_files == 1
    assert result.risks[-1].category == "maintainability"
    assert "placeholder.py" in result.risks[-1].evidence
