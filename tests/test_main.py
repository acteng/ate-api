from fastapi.testclient import TestClient

from ate_api.main import app

client = TestClient(app)


def test_index() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
