from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_skips_git_credentials_file(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".git-credentials").write_text(
        "https://user:secret@example.com/repo.git\n", encoding="utf-8"
    )

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
