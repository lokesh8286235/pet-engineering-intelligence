from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_skips_direnv_environment_file(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".envrc").write_text("export API_TOKEN=should-not-be-scanned\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
