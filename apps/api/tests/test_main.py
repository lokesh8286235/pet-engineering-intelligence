from pathlib import Path

import pytest

from app.main import _validate_allowed_root


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
