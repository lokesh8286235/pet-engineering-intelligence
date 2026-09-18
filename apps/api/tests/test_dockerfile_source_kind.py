from pathlib import Path

from app.analyzer import analyze_repository


def test_dockerfile_counts_as_source_artifact(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 1
    assert result.languages["Dockerfile"] == 1
    assert not any(r.message == "No source-code files detected" for r in result.risks)


def test_dockerfile_variants_count_as_source_artifacts(tmp_path: Path):
    (tmp_path / "Dockerfile.prod").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (tmp_path / "DOCKERFILE.dev").write_text("FROM node:22-alpine\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.source_files == 2
    assert result.languages["Dockerfile"] == 2
    assert not any(r.message == "No source-code files detected" for r in result.risks)
