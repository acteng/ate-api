from datetime import datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeRepository,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange


@respx.mock
def test_get_authority(authorities: AuthorityRepository, client: TestClient, access_token: str) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "abbreviation": "LIV",
        "fullName": "Liverpool City Region Combined Authority",
        "bidSubmittingCapitalSchemes": f"{client.base_url}/authorities/LIV/capital-schemes/bid-submitting",
    }


@respx.mock
def test_get_authority_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404


@respx.mock
def test_get_authority_bid_submitting_capital_schemes(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    capital_schemes.add(
        CapitalScheme(
            reference="ATE00001",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    capital_schemes.add(
        CapitalScheme(
            reference="ATE00002",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="School Streets",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    authorities.add(Authority(abbreviation="WYO", full_name="West Yorkshire Combined Authority"))
    capital_schemes.add(
        CapitalScheme(
            reference="ATE00003",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Hospital Fields Road",
                bid_submitting_authority="WYO",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
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


@respx.mock
def test_get_authority_bid_submitting_capital_schemes_when_none(
    authorities: AuthorityRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"items": []}


@respx.mock
def test_get_authority_bid_submitting_capital_schemes_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
