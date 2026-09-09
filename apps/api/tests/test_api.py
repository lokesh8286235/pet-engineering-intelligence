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
