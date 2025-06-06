from datetime import date, datetime, timezone

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


@respx.mock
def test_get_capital_scheme(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                bid_status=BidStatus.FUNDED,
            ),
        )
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
        "milestones": {
            "items": [],
        },
        "authorityReview": None,
    }


@respx.mock
def test_get_capital_scheme_with_milestones(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    capital_scheme = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=dummy_overview(),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
        )
    )
    capital_schemes.add(capital_scheme)

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["milestones"] == {
        "items": [
            {
                "milestone": "detailed design completed",
                "observationType": "actual",
                "statusDate": "2020-02-01",
            }
        ]
    }


@respx.mock
def test_get_capital_scheme_with_authority_review(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    capital_scheme = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=dummy_overview(),
        bid_status_details=dummy_bid_status_details(),
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
