from httpx import Client

from tests.e2e.app_client import AppClient


def test_get_capital_scheme(client: Client, access_token: str, app_client: AppClient) -> None:
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
            "milestones": {
                "items": [
                    {
                        "milestone": "detailed design completed",
                        "observationType": "actual",
                        "statusDate": "2020-03-01",
                    }
                ],
            },
            "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z"},
        }
    )

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/capital-schemes/ATE00001",
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
        "milestones": {
            "currentMilestone": "detailed design completed",
            "items": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2020-03-01",
                }
            ],
        },
        "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z"},
    }


def test_get_milestones(client: Client, access_token: str) -> None:
    response = client.get("/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            "public consultation completed",
            "feasibility design started",
            "feasibility design completed",
            "preliminary design completed",
            "outline design completed",
            "detailed design completed",
            "construction started",
            "construction completed",
            "funding completed",
            "not progressed",
            "superseded",
            "removed",
        ],
    }
