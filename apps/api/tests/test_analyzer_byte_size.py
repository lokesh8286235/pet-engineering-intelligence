from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_reports_utf8_byte_size_from_scanned_content(tmp_path: Path):
    content = "café 🚀\n"
    (tmp_path / "app.py").write_text(content, encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.signals[0].size_bytes == len(content.encode("utf-8"))
