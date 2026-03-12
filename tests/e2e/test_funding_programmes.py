from httpx import AsyncClient

from tests.e2e.app_client import AppClient


async def test_get_funding_programmes(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": True})
    app_client.create_funding_programme({"code": "ATF4", "eligibleForAuthorityUpdate": False})

    response = await client.get("/funding-programmes", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"@id": f"{client.base_url}/funding-programmes/ATF3", "code": "ATF3", "eligibleForAuthorityUpdate": True},
            {"@id": f"{client.base_url}/funding-programmes/ATF4", "code": "ATF4", "eligibleForAuthorityUpdate": False},
        ]
    }


async def test_get_funding_programme(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": True})

    response = await client.get("/funding-programmes/ATF3", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/funding-programmes/ATF3",
        "code": "ATF3",
        "eligibleForAuthorityUpdate": True,
    }
