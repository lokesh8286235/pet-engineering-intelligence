from pathlib import Path

from app.analyzer import MAX_SIGNALS, analyze_repository


def test_analyzer_reports_when_detailed_signals_are_truncated(tmp_path: Path):
    for index in range(MAX_SIGNALS + 1):
        (tmp_path / f"module_{index:03}.py").write_text("value = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=MAX_SIGNALS + 1)

    assert result.files == MAX_SIGNALS + 1
    assert len(result.signals) == MAX_SIGNALS
    assert any(
        risk.category == "analysis"
        and risk.severity == "low"
        and risk.message == "Detailed file signals truncated in the result"
        and risk.evidence == [f"signals={MAX_SIGNALS + 1}", f"returned_signals={MAX_SIGNALS}"]
        for risk in result.risks
    )
