from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_authority(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/authorities/LIV",
        "abbreviation": "LIV",
        "fullName": "Liverpool City Region Combined Authority",
        "bidSubmittingCapitalSchemes": f"{client.base_url}/authorities/LIV/capital-schemes/bid-submitting",
    }


def test_get_authority_bid_submitting_capital_schemes(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    app_client.create_capital_scheme(
        {
            "reference": "ATE00001",
            "overview": {
                "name": "Wirral Package",
                "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                "type": "construction",
            },
            "bidStatusDetails": {
                "bidStatus": "funded",
            },
            "financials": {
                "items": [],
            },
            "milestones": {
                "items": [],
            },
            "outputs": {
                "items": [],
            },
        }
    )
    app_client.create_capital_scheme(
        {
            "reference": "ATE00002",
            "overview": {
                "name": "School Streets",
                "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                "type": "construction",
            },
            "bidStatusDetails": {
                "bidStatus": "funded",
            },
            "financials": {
                "items": [],
            },
            "milestones": {
                "items": [],
            },
            "outputs": {
                "items": [],
            },
        }
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
            f"{client.base_url}/capital-schemes/ATE00002",
        ],
    }
