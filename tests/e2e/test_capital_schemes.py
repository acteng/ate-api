import asyncio

from httpx import AsyncClient

from tests.e2e.app_client import AppClient


async def test_get_capital_scheme(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.set_clock("2020-02-01T00:00:00Z")
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "outputs": {
                "items": [
                    {
                        "type": "widening existing footway",
                        "measure": "miles",
                        "observationType": "actual",
                        "value": "1.5",
                    }
                ]
            },
            "authorityReview": None,
        }
    )
    await app_client.create_capital_scheme_financial(
        "ATE00001", {"type": "spend to date", "amount": 2_000_000, "source": "ATF4 bid"}
    )
    await app_client.create_capital_scheme_milestones(
        "ATE00001",
        {
            "items": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2020-03-01",
                    "source": "ATF4 bid",
                }
            ]
        },
    )
    await app_client.create_capital_scheme_authority_review("ATE00001", {"source": "authority update"})

    response = await client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

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
        "bidStatusDetails": {"bidStatus": "funded"},
        "financials": {"items": [{"type": "spend to date", "amount": 2_000_000, "source": "ATF4 bid"}]},
        "milestones": {
            "currentMilestone": "detailed design completed",
            "items": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2020-03-01",
                    "source": "ATF4 bid",
                }
            ],
        },
        "outputs": {
            "items": [
                {
                    "type": "widening existing footway",
                    "measure": "miles",
                    "observationType": "actual",
                    "value": "1.500000",
                }
            ]
        },
        "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z", "source": "authority update"},
    }


async def test_create_financial(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "authorityReview": None,
        }
    )
    await app_client.create_capital_scheme_financial(
        "ATE00001", {"type": "spend to date", "amount": 2_000_000, "source": "ATF4 bid"}
    )

    response = await client.post(
        "/capital-schemes/ATE00001/financials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"type": "spend to date", "amount": 3_000_000, "source": "ATF4 bid"},
    )

    assert response.status_code == 201
    assert response.json() == {"type": "spend to date", "amount": 3_000_000, "source": "ATF4 bid"}
    capital_scheme = await app_client.get_capital_scheme("ATE00001")
    assert capital_scheme["financials"] == {
        "items": [{"type": "spend to date", "amount": 3_000_000, "source": "ATF4 bid"}]
    }


async def test_create_financial_concurrently(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "authorityReview": None,
        }
    )

    responses = await asyncio.gather(
        *[
            client.post(
                "/capital-schemes/ATE00001/financials",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"type": "spend to date", "amount": 3_000_000, "source": "ATF4 bid"},
            )
            for _ in range(3)
        ]
    )

    assert all(response.status_code == 201 for response in responses)
    capital_scheme = await app_client.get_capital_scheme("ATE00001")
    assert capital_scheme["financials"] == {
        "items": [{"type": "spend to date", "amount": 3_000_000, "source": "ATF4 bid"}]
    }


async def test_create_milestones(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "authorityReview": None,
        }
    )
    await app_client.create_capital_scheme_milestones(
        "ATE00001",
        {
            "items": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2020-02-01",
                    "source": "ATF4 bid",
                },
                {
                    "milestone": "construction started",
                    "observationType": "actual",
                    "statusDate": "2020-03-01",
                    "source": "ATF4 bid",
                },
            ]
        },
    )

    response = await client.post(
        "/capital-schemes/ATE00001/milestones",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "items": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2021-02-01",
                    "source": "ATF4 bid",
                },
                {
                    "milestone": "construction started",
                    "observationType": "actual",
                    "statusDate": "2021-03-01",
                    "source": "ATF4 bid",
                },
            ]
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "items": [
            {
                "milestone": "detailed design completed",
                "observationType": "actual",
                "statusDate": "2021-02-01",
                "source": "ATF4 bid",
            },
            {
                "milestone": "construction started",
                "observationType": "actual",
                "statusDate": "2021-03-01",
                "source": "ATF4 bid",
            },
        ]
    }
    capital_scheme = await app_client.get_capital_scheme("ATE00001")
    assert capital_scheme["milestones"]["items"] == [
        {
            "milestone": "detailed design completed",
            "observationType": "actual",
            "statusDate": "2021-02-01",
            "source": "ATF4 bid",
        },
        {
            "milestone": "construction started",
            "observationType": "actual",
            "statusDate": "2021-03-01",
            "source": "ATF4 bid",
        },
    ]


async def test_create_milestones_concurrently(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": False})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "authorityReview": None,
        }
    )

    responses = await asyncio.gather(
        *[
            client.post(
                "/capital-schemes/ATE00001/milestones",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "items": [
                        {
                            "milestone": "detailed design completed",
                            "observationType": "actual",
                            "statusDate": "2021-02-01",
                            "source": "ATF4 bid",
                        }
                    ]
                },
            )
            for _ in range(3)
        ]
    )

    assert all(response.status_code == 201 for response in responses)
    capital_scheme = await app_client.get_capital_scheme("ATE00001")
    assert capital_scheme["milestones"]["items"] == [
        {
            "milestone": "detailed design completed",
            "observationType": "actual",
            "statusDate": "2021-02-01",
            "source": "ATF4 bid",
        }
    ]


async def test_create_authority_review(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.set_clock("2020-02-01T00:00:00Z")
    await app_client.create_funding_programme({"code": "ATF3", "eligibleForAuthorityUpdate": True})
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_capital_scheme(
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
            "authorityReview": None,
        }
    )
    await app_client.create_capital_scheme_authority_review("ATE00001", {"source": "ATF4 bid"})
    await app_client.set_clock("2021-02-01T00:00:00Z")

    response = await client.post(
        "/capital-schemes/ATE00001/authority-reviews",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"source": "authority update"},
    )

    assert response.status_code == 201
    assert response.json() == {"reviewDate": "2021-02-01T00:00:00Z", "source": "authority update"}
    capital_scheme = await app_client.get_capital_scheme("ATE00001")
    assert capital_scheme["authorityReview"] == {"reviewDate": "2021-02-01T00:00:00Z", "source": "authority update"}


async def test_get_milestones(client: AsyncClient, access_token: str) -> None:
    response = await client.get("/capital-schemes/milestones", headers={"Authorization": f"Bearer {access_token}"})

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
        ]
    }
