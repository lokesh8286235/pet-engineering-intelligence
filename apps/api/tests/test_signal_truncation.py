from pathlib import Path

from app.analyzer import analyze_repository


def test_api_analyzer_discloses_capped_file_signals(tmp_path: Path):
    for index in range(101):
        (tmp_path / f"module_{index:03d}.py").write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=101)

    assert result.files == 101
    assert len(result.signals) == 100
    assert any(
        risk.category == "analysis"
        and risk.severity == "low"
        and risk.message == "Detailed file signals truncated in the result"
        and risk.evidence == ["signals=101", "returned_signals=100"]
        for risk in result.risks
    )
