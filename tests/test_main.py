from fastapi.testclient import TestClient

from ate_api.main import app

client = TestClient(app)


def test_get_index() -> None:
    response = client.get("/", headers={"Authorization": "Bearer 123"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_cannot_get_index_without_bearer() -> None:
    response = client.get("/")

    assert response.status_code == 403
