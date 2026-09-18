from pathlib import Path

from app.analyzer import analyze_repository


def test_kotlin_and_swift_count_as_source_artifacts(tmp_path: Path):
    (tmp_path / "Main.kt").write_text("fun main() = println(\"ok\")\n", encoding="utf-8")
    (tmp_path / "App.swift").write_text("import Foundation\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.source_files == 2
    assert result.languages["Kotlin"] == 1
    assert result.languages["Swift"] == 1
    assert not any(r.message == "No source-code files detected" for r in result.risks)
