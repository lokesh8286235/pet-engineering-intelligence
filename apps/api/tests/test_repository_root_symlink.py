from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_rejects_symlink_path_outside_configured_repository_root(tmp_path, monkeypatch):
    allowed = tmp_path / "workspace"
    outside = tmp_path / "outside"
    link = allowed / "linked-repo"
    allowed.mkdir()
    outside.mkdir()
    (outside / "app.py").write_text("secret = True\n", encoding="utf-8")
    link.symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("PET_REPOSITORY_ROOT", str(allowed))

    response = client.post("/v1/analyze", json={"path": str(link)})

    assert response.status_code == 400
    assert response.json()["detail"] == "path must be within PET_REPOSITORY_ROOT"
