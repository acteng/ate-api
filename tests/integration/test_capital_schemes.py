from datetime import UTC, date, datetime
from decimal import Decimal

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancial,
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
)
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.clock import Clock
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


@respx.mock
async def test_get_capital_scheme(
    authorities: AuthorityRepository,
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                bid_status=BidStatus.FUNDED,
            ),
        )
    )
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

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
        "financials": {
            "items": [],
        },
        "milestones": {
            "currentMilestone": None,
            "items": [],
        },
        "outputs": {
            "items": [],
        },
        "authorityReview": None,
    }


@respx.mock
async def test_get_capital_scheme_with_financials(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
    )
    financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
    financials.adjust_financial(
        CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_financials.add(financials)

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["financials"] == {
        "items": [
            {
                "type": "funding allocation",
                "amount": 2_000_000,
                "source": "ATF4 bid",
            }
        ],
    }


@respx.mock
async def test_get_capital_scheme_with_milestones(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    client: TestClient,
    access_token: str,
) -> None:
    capital_scheme = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=dummy_overview(),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme)
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["milestones"] == {
        "currentMilestone": "detailed design completed",
        "items": [
            {
                "milestone": "detailed design completed",
                "observationType": "actual",
                "statusDate": "2020-02-01",
                "source": "ATF4 bid",
            }
        ],
    }


@respx.mock
async def test_get_capital_scheme_with_outputs(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    client: TestClient,
    access_token: str,
) -> None:
    capital_scheme = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=dummy_overview(),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme.change_output(
        CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )
    )
    await capital_schemes.add(capital_scheme)
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["outputs"] == {
        "items": [
            {
                "type": "widening existing footway",
                "measure": "miles",
                "observationType": "actual",
                "value": "1.5",
            }
        ],
    }


@respx.mock
async def test_get_capital_scheme_with_authority_review(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    client: TestClient,
    access_token: str,
) -> None:
    capital_scheme = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=dummy_overview(),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1, tzinfo=UTC)))
    await capital_schemes.add(capital_scheme)
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["authorityReview"] == {"reviewDate": "2020-02-01T00:00:00Z"}


@respx.mock
def test_get_capital_scheme_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404


@respx.mock
async def test_create_financial_creates_financial(
    clock: Clock, capital_scheme_financials: CapitalSchemeFinancialsRepository, client: TestClient, access_token: str
) -> None:
    clock.now = datetime(2020, 1, 1, tzinfo=UTC)
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

    client.post(
        "/capital-schemes/ATE00001/financials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "funding allocation",
            "amount": 3_000_000,
            "source": "ATF4 bid",
        },
    )

    financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
    assert financials and financials.financials == [
        CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(3_000_000),
            data_source=DataSource.ATF4_BID,
        )
    ]


@respx.mock
async def test_create_financial_closes_current_financial(
    clock: Clock, capital_scheme_financials: CapitalSchemeFinancialsRepository, client: TestClient, access_token: str
) -> None:
    clock.now = datetime(2020, 2, 1, tzinfo=UTC)
    financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
    financials.change_financial(
        CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_financials.add(financials)

    client.post(
        "/capital-schemes/ATE00001/financials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "funding allocation",
            "amount": 3_000_000,
            "source": "ATF4 bid",
        },
    )

    actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
    assert actual_financials and actual_financials.financials[0].effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)


@respx.mock
async def test_create_financial_returns_created_financial(
    capital_scheme_financials: CapitalSchemeFinancialsRepository, client: TestClient, access_token: str
) -> None:
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))

    response = client.post(
        "/capital-schemes/ATE00001/financials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "funding allocation",
            "amount": 3_000_000,
            "source": "ATF4 bid",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "type": "funding allocation",
        "amount": 3_000_000,
        "source": "ATF4 bid",
    }


@respx.mock
def test_create_financial_when_capital_scheme_not_found(client: TestClient, access_token: str) -> None:
    response = client.post(
        "/capital-schemes/ATE00001/financials",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "funding allocation",
            "amount": 3_000_000,
            "source": "ATF4 bid",
        },
    )

    assert response.status_code == 404


@respx.mock
async def test_get_milestones(client: TestClient, access_token: str) -> None:
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


@respx.mock
async def test_get_milestones_filters_by_active(client: TestClient, access_token: str) -> None:
    response = client.get(
        "/capital-schemes/milestones?active=true", headers={"Authorization": f"Bearer {access_token}"}
    )

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
        ],
    }


@respx.mock
async def test_get_milestones_filters_by_complete(client: TestClient, access_token: str) -> None:
    response = client.get(
        "/capital-schemes/milestones?complete=true", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            "funding completed",
        ],
    }
