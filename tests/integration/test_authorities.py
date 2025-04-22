from datetime import datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeRepository,
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
        "bidSubmittingCapitalSchemes": "/authorities/LIV/capital-schemes/bid-submitting",
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
    capital_scheme1 = CapitalScheme(reference="ATE00001")
    capital_scheme1.update_overview(
        CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
    )
    capital_schemes.add(capital_scheme1)
    capital_scheme2 = CapitalScheme(reference="ATE00002")
    capital_scheme2.update_overview(
        CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
    )
    capital_schemes.add(capital_scheme2)
    authorities.add(Authority(abbreviation="WYO", full_name="West Yorkshire Combined Authority"))
    capital_scheme3 = CapitalScheme(reference="ATE00003")
    capital_scheme3.update_overview(
        CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="WYO")
    )
    capital_schemes.add(capital_scheme3)

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
