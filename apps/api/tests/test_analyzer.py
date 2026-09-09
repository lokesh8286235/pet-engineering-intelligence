from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_counts_languages_and_lines(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 2
    assert result.lines == 2
    assert result.languages["Python"] == 1
    assert result.languages["Markdown"] == 1


def test_analyzer_flags_missing_tests(tmp_path: Path):
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert any(r.category == "testing" and r.severity == "high" for r in result.risks)


def test_analyzer_skips_symlinks(tmp_path: Path):
    target = tmp_path / "outside.py"
    target.write_text("secret = True\n", encoding="utf-8")
    link = tmp_path / "linked.py"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        return
    result = analyze_repository(str(tmp_path))
    assert all(signal.path != "linked.py" for signal in result.signals)


def test_analyzer_skips_binary_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"\x89PNG\r\n\x1a\n\x00binary")
    result = analyze_repository(str(tmp_path))
    assert result.files == 1
    assert all(signal.path != "image.bin" for signal in result.signals)
