from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_detects_plural_test_and_spec_filenames(tmp_path: Path) -> None:
    (tmp_path / "integration_tests.py").write_text("def test_integration(): pass\n", encoding="utf-8")
    (tmp_path / "api_specs.py").write_text("def test_api_contract(): pass\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert not any(r.category == "testing" for r in result.risks)
