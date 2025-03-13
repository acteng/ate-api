from fastapi.testclient import TestClient


def test_get_index(client: TestClient) -> None:
    response = client.get("/", headers={"Authorization": "Bearer 123"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_cannot_get_index_without_bearer(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 403
