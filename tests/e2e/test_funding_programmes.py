from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_funding_programmes(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    app_client.create_funding_programme({"code": "ATF4", "eligibleForAuthorityUpdate": False})

    response = client.get("/funding-programmes", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"@id": f"{client.base_url}/funding-programmes/ATF3", "code": "ATF3"},
            {"@id": f"{client.base_url}/funding-programmes/ATF4", "code": "ATF4"},
        ]
    }


def test_get_funding_programme(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": True})

    response = client.get("/funding-programmes/ATF3", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/funding-programmes/ATF3",
        "code": "ATF3",
        "eligibleForAuthorityUpdate": True,
    }
