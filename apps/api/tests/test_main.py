from pathlib import Path

import pytest
from fastapi import Response

from app.main import _cors_origins, _validate_allowed_root, health


def test_validate_allowed_root_accepts_repository_descendant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "workspace"
    repository = root / "project"
    repository.mkdir(parents=True)
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(root))

    _validate_allowed_root(str(repository))


def test_validate_allowed_root_rejects_paths_outside_configured_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "workspace"
    outside = tmp_path / "workspace-escape"
    root.mkdir()
    outside.mkdir()
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(root))

    with pytest.raises(ValueError, match="within PET_REPOSITORY_ROOT"):
        _validate_allowed_root(str(outside))


def test_validate_allowed_root_rejects_symlink_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "workspace"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    escaped = root / "project"
    escaped.symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(root))

    with pytest.raises(ValueError, match="within PET_REPOSITORY_ROOT"):
        _validate_allowed_root(str(escaped))


def test_health_prevents_caching() -> None:
    response = Response()

    payload = health(response)

    assert payload == {"status": "ok", "service": "pet-api"}
    assert response.headers["Cache-Control"] == "no-store"


def test_cors_origins_support_multiple_configured_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PET_CORS_ORIGINS", "https://app.example.com, https://admin.example.com")

    assert _cors_origins() == ["https://app.example.com", "https://admin.example.com"]


def test_cors_origins_falls_back_when_configuration_is_blank(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PET_CORS_ORIGINS", "  ,  ")

    assert _cors_origins() == ["http://localhost:3000"]
