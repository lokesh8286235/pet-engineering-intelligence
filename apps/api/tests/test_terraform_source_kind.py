from pathlib import Path

from app.analyzer import analyze_repository


def test_terraform_files_count_as_source_artifacts(tmp_path: Path):
    (tmp_path / "main.tf").write_text('resource "aws_s3_bucket" "example" {}\n', encoding="utf-8")
    (tmp_path / "variables.tf").write_text('variable "region" {}\n', encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.source_files == 2
    assert result.languages["Terraform"] == 2
    assert not any(r.message == "No source-code files detected" for r in result.risks)
