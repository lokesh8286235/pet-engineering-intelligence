from pathlib import Path

from app.analyzer import MAX_SIGNALS, analyze_repository


def test_large_scan_counts_all_files_without_retaining_all_signals(tmp_path: Path):
    for index in range(MAX_SIGNALS + 25):
        (tmp_path / f"module_{index}.py").write_text("print('ok')\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == MAX_SIGNALS + 25
    assert result.source_files == MAX_SIGNALS + 25
    assert len(result.signals) == MAX_SIGNALS
    assert any(r.message == "Detailed file signals truncated in the result" for r in result.risks)
