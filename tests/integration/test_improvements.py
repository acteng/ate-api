from datetime import UTC, datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from ate_api.domain.improvements.overviews import ImprovementOverview
from tests.unit.domain.builders import build_authority


@respx.mock
async def test_get_improvement(
    authorities: AuthorityRepository,
    improvements: ImprovementRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))
    await improvements.add(
        Improvement(
            reference=ImprovementReference("IMP00001"),
            overview=ImprovementOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                funding_managed_by=AuthorityAbbreviation("LIV"),
                data_source=DataSource.AUTHORITY_UPDATE,
            ),
        )
    )

    response = client.get("/improvements/IMP00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/improvements/IMP00001",
        "reference": "IMP00001",
        "overview": {
            "name": "Wirral Package",
            "description": 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            "fundingManagedBy": f"{client.base_url}/authorities/LIV",
            "source": "authority update",
        },
    }


@respx.mock
def test_get_improvement_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/improvements/IMP00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
