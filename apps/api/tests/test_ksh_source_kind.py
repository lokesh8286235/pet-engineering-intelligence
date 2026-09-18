from pathlib import Path

from app.analyzer import analyze_repository


def test_ksh_scripts_are_classified_as_shell_source(tmp_path: Path):
    (tmp_path / "deploy.ksh").write_text("echo deploy\n", encoding="utf-8")
    (tmp_path / "bootstrap.sh").write_text("echo bootstrap\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.languages["Shell"] == 2
    assert result.source_files == 2
    assert all(signal.kind == "Shell" for signal in result.signals)
