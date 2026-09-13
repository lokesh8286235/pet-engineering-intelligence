from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_ignores_os_metadata_files_case_insensitively(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".DS_Store").write_text("desktop metadata\n", encoding="utf-8")
    (tmp_path / "Thumbs.db").write_text("thumbnail metadata\n", encoding="utf-8")

    nested = tmp_path / "docs"
    nested.mkdir()
    (nested / ".ds_store").write_text("desktop metadata\n", encoding="utf-8")
    (nested / "thumbs.DB").write_text("thumbnail metadata\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
