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


def test_get_authority_bid_submitting_capital_schemes(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3"})
    app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    app_client.create_capital_scheme(
        {
            "reference": "ATE00001",
            "overview": {
                "effectiveDate": {"from": "2020-01-01T00:00:00+00:00"},
                "name": "Wirral Package",
                "bidSubmittingAuthority": "/authorities/LIV",
                "fundingProgramme": "/funding-programmes/ATF3",
                "type": "construction",
            },
        }
    )
    app_client.create_capital_scheme(
        {
            "reference": "ATE00002",
            "overview": {
                "effectiveDate": {"from": "2020-01-01T00:00:00+00:00"},
                "name": "School Streets",
                "bidSubmittingAuthority": "/authorities/LIV",
                "fundingProgramme": "/funding-programmes/ATF3",
                "type": "construction",
            },
        }
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            "/capital-schemes/ATE00001",
            "/capital-schemes/ATE00002",
        ],
    }
