from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_classifies_common_web_assets_as_source(tmp_path: Path):
    (tmp_path / "index.html").write_text("<main>Hello</main>\n", encoding="utf-8")
    (tmp_path / "theme.css").write_text("body { margin: 0; }\n", encoding="utf-8")
    (tmp_path / "tokens.scss").write_text("$gap: 8px;\n", encoding="utf-8")
    (tmp_path / "legacy.sass").write_text("body\n  margin: 0\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.languages["HTML"] == 1
    assert result.languages["CSS"] == 3
    assert result.source_files == 4
    assert all(signal.kind in {"HTML", "CSS"} for signal in result.signals)
