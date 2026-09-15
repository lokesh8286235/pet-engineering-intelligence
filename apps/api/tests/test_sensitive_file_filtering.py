from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_skips_sensitive_filenames_case_insensitively(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in (".ENV", "Credentials.JSON", "SERVER.PEM", "ID_RSA"):
        (tmp_path / name).write_text("SECRET=should-not-be-scanned\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
