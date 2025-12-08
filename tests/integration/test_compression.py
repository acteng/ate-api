from datetime import UTC, date, datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFinancialsRepository
from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestone,
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
)
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


@respx.mock
async def test_can_request_uncompressed_response(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
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
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))
    await capital_scheme_milestones.add(
        _build_capital_scheme_milestones(capital_scheme=CapitalSchemeReference("ATE00001"))
    )

    response = client.get(
        "/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}", "Accept-Encoding": "identity"}
    )

    assert response.status_code == 200 and "Content-Encoding" not in response.headers


@respx.mock
async def test_can_request_compressed_response(
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
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
    await capital_scheme_financials.add(CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001")))
    await capital_scheme_milestones.add(
        _build_capital_scheme_milestones(capital_scheme=CapitalSchemeReference("ATE00001"))
    )

    response = client.get(
        "/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}", "Accept-Encoding": "gzip"}
    )

    assert response.status_code == 200 and response.headers["Content-Encoding"] == "gzip"


def _build_capital_scheme_milestones(capital_scheme: CapitalSchemeReference) -> CapitalSchemeMilestones:
    # Representation must be >= 500 bytes for it to be compressed
    milestones = CapitalSchemeMilestones(capital_scheme=capital_scheme)
    milestones.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    milestones.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    return milestones
