from pathlib import Path

from app.analyzer import analyze_repository


def test_dockerfile_counts_as_source_artifact(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 1
    assert result.languages["Dockerfile"] == 1
    assert not any(r.message == "No source-code files detected" for r in result.risks)
