from datetime import datetime, timezone

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeRepository,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange


@respx.mock
def test_get_capital_scheme(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    capital_schemes.add(
        CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type_=CapitalSchemeType.CONSTRUCTION,
        )
    )

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "reference": "ATE00001",
        "overview": {
            "effectiveDate": {"from": "2020-01-01T00:00:00Z", "to": None},
            "name": "Wirral Package",
            "bidSubmittingAuthority": "/authorities/LIV",
            "fundingProgramme": "/funding-programmes/ATF3",
            "type": "construction",
        },
    }


@respx.mock
def test_get_capital_scheme_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
