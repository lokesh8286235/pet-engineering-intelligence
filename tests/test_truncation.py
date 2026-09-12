from pathlib import Path

from app.analyzer import analyze_repository


def test_truncated_scan_reduces_health_score(tmp_path: Path):
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=1)

    assert result.files == 1
    assert result.health_score == 65
    risk = next(r for r in result.risks if r.category == "analysis")
    assert risk.severity == "low"
