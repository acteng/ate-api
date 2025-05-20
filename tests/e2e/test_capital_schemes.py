from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_capital_scheme(client: Client, access_token: str, app_client: AppClient) -> None:
    app_client.create_funding_programme({"code": "ATF3"})
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
            "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z"},
        }
    )

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
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
        "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z"},
    }
