from pathlib import Path

from app.analyzer import analyze_repository


def test_c_family_files_are_counted_as_source(tmp_path: Path) -> None:
    (tmp_path / "main.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
    (tmp_path / "widget.cpp").write_text("int widget() { return 1; }\n", encoding="utf-8")
    (tmp_path / "widget.hpp").write_text("int widget();\n", encoding="utf-8")
    (tmp_path / "Program.cs").write_text("class Program {}\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.source_files == 4
    assert result.languages["C"] == 1
    assert result.languages["C++"] == 2
    assert result.languages["C#"] == 1
