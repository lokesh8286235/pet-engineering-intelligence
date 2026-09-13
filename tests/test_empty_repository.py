from pathlib import Path

from app.analyzer import analyze_repository


def test_empty_repository_is_not_reported_as_healthy(tmp_path: Path) -> None:
    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.lines == 0
    assert result.health_score == 0
    assert any(
        risk.category == "analysis" and risk.severity == "high"
        for risk in result.risks
    )
