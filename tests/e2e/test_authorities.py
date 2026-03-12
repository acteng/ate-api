from httpx import AsyncClient

from tests.e2e.app_client import AppClient


async def test_get_authority(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})

    response = await client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/authorities/LIV",
        "abbreviation": "LIV",
        "fullName": "Liverpool City Region Combined Authority",
        "bidSubmittingCapitalSchemes": f"{client.base_url}/authorities/LIV/capital-schemes/bid-submitting",
    }


async def test_get_authority_bid_submitting_capital_schemes(
    client: AsyncClient, access_token: str, app_client: AppClient
) -> None:
    app_client.set_clock("2020-02-01T00:00:00Z")
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
            "bidStatusDetails": {"bidStatus": "funded"},
            "financials": {"items": []},
            "milestones": {"items": []},
            "outputs": {"items": []},
        }
    )
    app_client.create_capital_scheme_authority_review("ATE00001", {"source": "authority update"})
    app_client.create_capital_scheme(
        {
            "reference": "ATE00002",
            "overview": {
                "name": "School Streets",
                "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                "type": "construction",
            },
            "bidStatusDetails": {"bidStatus": "funded"},
            "financials": {"items": []},
            "milestones": {"items": []},
            "outputs": {"items": []},
        }
    )

    response = await client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "@id": f"{client.base_url}/capital-schemes/ATE00001",
                "reference": "ATE00001",
                "overview": {
                    "name": "Wirral Package",
                    "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                    "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                    "type": "construction",
                },
                "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z", "source": "authority update"},
            },
            {
                "@id": f"{client.base_url}/capital-schemes/ATE00002",
                "reference": "ATE00002",
                "overview": {
                    "name": "School Streets",
                    "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                    "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                    "type": "construction",
                },
                "authorityReview": None,
            },
        ]
    }
