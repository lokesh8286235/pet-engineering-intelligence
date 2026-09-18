from pathlib import Path

from app.analyzer import analyze_repository


def test_shell_scripts_count_as_source_artifacts(tmp_path: Path):
    (tmp_path / "deploy.sh").write_text("#!/usr/bin/env bash\necho deploy\n", encoding="utf-8")
    (tmp_path / "bootstrap.bash").write_text("echo bootstrap\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.source_files == 2
    assert result.languages["Shell"] == 2
    assert not any(r.message == "No source-code files detected" for r in result.risks)
