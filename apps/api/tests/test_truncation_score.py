from pathlib import Path

from app.analyzer import analyze_repository


def test_truncated_scan_reduces_health_score(tmp_path: Path):
    for name in ("a.py", "b.py", "c.py"):
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_app(): pass\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=4)

    assert result.files == 4
    assert any(r.category == "analysis" for r in result.risks)
    assert result.health_score == 90
