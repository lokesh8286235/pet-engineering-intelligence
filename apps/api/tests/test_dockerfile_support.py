from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_recognizes_dockerfile(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12-slim\nWORKDIR /app\n",
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 0
    assert result.languages["Dockerfile"] == 1
    assert result.signals[0].kind == "Dockerfile"
