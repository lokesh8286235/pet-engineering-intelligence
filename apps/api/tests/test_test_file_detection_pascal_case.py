from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_detects_pascal_case_test_files(tmp_path: Path):
    (tmp_path / "TestParser.py").write_text("def test_parser(): pass\n", encoding="utf-8")
    (tmp_path / "contest.py").write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert not any(r.category == "testing" for r in result.risks)
