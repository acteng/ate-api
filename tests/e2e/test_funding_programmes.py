from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_funding_programme(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3"})

    response = client.get("/funding-programmes/ATF3", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"code": "ATF3"}
