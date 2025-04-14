from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_authority(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "abbreviation": "LIV",
        "fullName": "Liverpool City Region Combined Authority",
        "bidSubmittingCapitalSchemes": "/authorities/LIV/capital-schemes/bid-submitting",
    }
