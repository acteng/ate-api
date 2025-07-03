import respx
from fastapi.testclient import TestClient

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository


@respx.mock
async def test_get_funding_programmes(
    funding_programmes: FundingProgrammeRepository, client: TestClient, access_token: str
) -> None:
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))

    response = client.get("/funding-programmes", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/funding-programmes/ATF3",
            f"{client.base_url}/funding-programmes/ATF4",
        ]
    }


@respx.mock
async def test_get_funding_programme(
    funding_programmes: FundingProgrammeRepository, client: TestClient, access_token: str
) -> None:
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

    response = client.get("/funding-programmes/ATF3", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"code": "ATF3"}


@respx.mock
def test_get_funding_programme_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/funding-programmes/ATF3", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
