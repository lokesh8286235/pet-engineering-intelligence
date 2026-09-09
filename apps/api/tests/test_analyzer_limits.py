from pathlib import Path

from app.analyzer import analyze_repository


def test_analysis_preserves_total_file_count_when_signals_are_capped(tmp_path: Path):
    for index in range(3):
        (tmp_path / f"file{index}.py").write_text(f"value = {index}\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=3)

    assert result.files == 3
    assert len(result.signals) == 3
