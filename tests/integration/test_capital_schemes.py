from datetime import datetime, timezone

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.domain.capital_schemes.bid_statuses import (
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
)
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.overviews import (
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


@respx.mock
def test_get_capital_scheme(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    capital_schemes.add(
        CapitalScheme(
            reference="ATE00001",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                bid_status=CapitalSchemeBidStatus.FUNDED,
            ),
        )
    )

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "reference": "ATE00001",
        "overview": {
            "effectiveDate": {"from": "2020-01-01T00:00:00Z", "to": None},
            "name": "Wirral Package",
            "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
            "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
            "type": "construction",
        },
        "bidStatusDetails": {
            "effectiveDate": {"from": "2020-02-01T00:00:00Z", "to": None},
            "bidStatus": "funded",
        },
        "authorityReview": None,
    }


@respx.mock
def test_get_capital_scheme_with_authority_review(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))
    capital_scheme = CapitalScheme(
        reference="ATE00001", overview=dummy_overview(), bid_status_details=dummy_bid_status_details()
    )
    capital_scheme.perform_authority_review(
        CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1, tzinfo=timezone.utc))
    )
    capital_schemes.add(capital_scheme)

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["authorityReview"] == {"reviewDate": "2020-02-01T00:00:00Z"}


@respx.mock
def test_get_capital_scheme_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
