from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_flags_documentation_only_repository(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Documentation\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 0
    risk = next(r for r in result.risks if r.category == "analysis")
    assert risk.message == "No source files detected"
    assert risk.evidence == ["source_files=0"]
    assert result.health_score == 55


def test_analyzer_scores_empty_repository_as_unanalyzable(tmp_path: Path):
    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.source_files == 0
    risk = next(r for r in result.risks if r.category == "analysis")
    assert risk.severity == "high"
    assert risk.message == "No analyzable text files detected"
    assert risk.evidence == ["files=0"]
    assert result.health_score == 0
