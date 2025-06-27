from datetime import date, datetime, timezone

import respx
from fastapi.testclient import TestClient

from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


@respx.mock
async def test_can_request_uncompressed_response(
    capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await capital_schemes.add(_build_capital_scheme(reference=CapitalSchemeReference("ATE00001")))

    response = client.get(
        "/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}", "Accept-Encoding": "identity"}
    )

    assert response.status_code == 200 and "Content-Encoding" not in response.headers


@respx.mock
async def test_can_request_compressed_response(
    capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await capital_schemes.add(_build_capital_scheme(reference=CapitalSchemeReference("ATE00001")))

    response = client.get(
        "/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}", "Accept-Encoding": "gzip"}
    )

    assert response.status_code == 200 and response.headers["Content-Encoding"] == "gzip"


def _build_capital_scheme(reference: CapitalSchemeReference) -> CapitalScheme:
    # Representation must be >= 500 bytes for it to be compressed
    capital_scheme = CapitalScheme(
        reference=reference,
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
    capital_scheme.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
        )
    )
    return capital_scheme
