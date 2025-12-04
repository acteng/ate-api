from datetime import UTC, date, datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details


@respx.mock
async def test_get_authority(authorities: AuthorityRepository, client: TestClient, access_token: str) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/authorities/LIV",
        "abbreviation": "LIV",
        "fullName": "Liverpool City Region Combined Authority",
        "bidSubmittingCapitalSchemes": f"{client.base_url}/authorities/LIV/capital-schemes/bid-submitting",
    }


@respx.mock
def test_get_authority_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
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
            bid_status_details=dummy_bid_status_details(),
        )
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
    )
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("WYO"), full_name="West Yorkshire Combined Authority")
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("WYO"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
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
async def test_get_authority_bid_submitting_capital_schemes_filters_by_funding_programme(
    authorities: AuthorityRepository,
    funding_programmes: FundingProgrammeRepository,
    capital_schemes: CapitalSchemeRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))
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
            bid_status_details=dummy_bid_status_details(),
        )
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": "ATF3"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_funding_programmes(
    authorities: AuthorityRepository,
    funding_programmes: FundingProgrammeRepository,
    capital_schemes: CapitalSchemeRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF5")))
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
            bid_status_details=dummy_bid_status_details(),
        )
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF5"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": ["ATF3", "ATF4"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
            f"{client.base_url}/capital-schemes/ATE00002",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filter_by_unknown_funding_programme(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": "foo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_bid_status(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
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
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
            ),
        )
    )
    await capital_schemes.add(
        CapitalScheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.NOT_FUNDED
            ),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"bid-status": "funded"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filter_by_unknown_bid_status(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"bid-status": "foo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_current_milestone(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    capital_scheme1 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme1.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme1)
    capital_scheme2 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00002"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme2)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": "detailed design completed"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_current_milestones(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    capital_scheme1 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme1.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme1)
    capital_scheme2 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00002"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme2)
    capital_scheme3 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00003"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Hospital Fields Road",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme3.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 4, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme3)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": ["detailed design completed", "construction started"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
            f"{client.base_url}/capital-schemes/ATE00002",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_no_current_milestone(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
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
            bid_status_details=dummy_bid_status_details(),
        )
    )
    capital_scheme2 = CapitalScheme(
        reference=CapitalSchemeReference("ATE00002"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
        bid_status_details=dummy_bid_status_details(),
    )
    capital_scheme2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_schemes.add(capital_scheme2)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            f"{client.base_url}/capital-schemes/ATE00001",
        ],
    }


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filter_by_unknown_current_milestone(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": "foo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_when_none(
    authorities: AuthorityRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

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
