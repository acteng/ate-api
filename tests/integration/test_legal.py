from starlette.testclient import TestClient


def test_security(client: TestClient) -> None:
    response = client.get("/.well-known/security.txt")

    assert response.status_code == 200 and response.headers["content-type"] == "text/plain; charset=utf-8"
