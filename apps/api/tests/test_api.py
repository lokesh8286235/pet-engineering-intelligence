from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_rejects_invalid_max_files(tmp_path):
    response = client.post("/v1/analyze", json={"path": str(tmp_path), "max_files": 0})

    assert response.status_code == 400
    assert response.json()["detail"] == "max_files must be greater than zero"


def test_analyze_rejects_non_directory_path(tmp_path):
    file_path = tmp_path / "not-a-directory.txt"
    file_path.write_text("content", encoding="utf-8")

    response = client.post("/v1/analyze", json={"path": str(file_path)})

    assert response.status_code == 400
    assert response.json()["detail"] == "path must point to an existing directory"


def test_analyze_rejects_paths_outside_configured_repository_root(tmp_path, monkeypatch):
    allowed = tmp_path / "workspace"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    (outside / "app.py").write_text("secret = True\n", encoding="utf-8")
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(allowed))

    response = client.post("/v1/analyze", json={"path": str(outside)})

    assert response.status_code == 400
    assert response.json()["detail"] == "path must be within PET_REPOSITORY_ROOT"


def test_analyze_accepts_path_inside_configured_repository_root(tmp_path, monkeypatch):
    allowed = tmp_path / "workspace"
    repo = allowed / "repo"
    allowed.mkdir()
    repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(allowed))

    response = client.post("/v1/analyze", json={"path": str(repo)})

    assert response.status_code == 200
    assert response.json()["files"] == 1
