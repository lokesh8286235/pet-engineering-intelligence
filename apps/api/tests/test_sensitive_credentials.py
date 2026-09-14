from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_skips_git_credentials_and_key_material(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in (".git-credentials", "deploy.key", "client.p12", "client.pfx"):
        (tmp_path / name).write_text("SECRET=should-not-be-scanned\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
    assert all(
        signal.path not in {".git-credentials", "deploy.key", "client.p12", "client.pfx"}
        for signal in result.signals
    )
