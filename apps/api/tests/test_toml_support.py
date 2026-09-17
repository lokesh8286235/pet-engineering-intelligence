from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_recognizes_toml_project_files(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages["TOML"] == 1
    assert result.signals[0].kind == "TOML"
