from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_classifies_vue_and_svelte_as_source_files(tmp_path: Path):
    (tmp_path / "App.vue").write_text("<template><main /></template>\n", encoding="utf-8")
    (tmp_path / "Widget.svelte").write_text("<script>let count = 0;</script>\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.source_files == 2
    assert result.languages["Vue"] == 1
    assert result.languages["Svelte"] == 1
