from pathlib import Path

from app.analyzer import analyze_repository


def test_whitespace_only_source_is_reported_as_empty(tmp_path: Path):
    (tmp_path / "placeholder.py").write_text("  \n\t\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.source_files == 1
    maintainability_risks = [risk for risk in result.risks if risk.category == "maintainability"]
    assert maintainability_risks
    assert any("placeholder.py" in risk.evidence for risk in maintainability_risks)
