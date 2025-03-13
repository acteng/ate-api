from httpx import Client


def test_get_index(client: Client) -> None:
    response = client.get("/", headers={"Authorization": "Bearer 123"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
