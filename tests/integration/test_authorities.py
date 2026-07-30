from datetime import UTC, date, datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestone,
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
)
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.builders import build_capital_scheme


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
    authorities: AuthorityRepository,
    improvements: ImprovementRepository,
    capital_schemes: CapitalSchemeRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await improvements.add(
        Improvement(
            reference=ImprovementReference("IMP00001"),
            overview=ImprovementOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                funding_managed_by=AuthorityAbbreviation("LIV"),
                description="Improvement for the 'Wirral Package' capital scheme created as part of funding devolution.",
                data_source=DataSource.AUTHORITY_UPDATE,
            ),
        )
    )
    capital_scheme = build_capital_scheme(
        reference=CapitalSchemeReference("ATE00001"),
        overview=CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        ),
    )
    capital_scheme.perform_authority_review(
        CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
    )
    await capital_schemes.add(capital_scheme)
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=ImprovementReference("IMP00001"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("WYO"), full_name="West Yorkshire Combined Authority")
    )
    await improvements.add(
        Improvement(
            reference=ImprovementReference("IMP00002"),
            overview=ImprovementOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                funding_managed_by=AuthorityAbbreviation("WYO"),
                description="Improvement for the 'Hospital Fields Road' capital scheme created as part of funding devolution.",
                data_source=DataSource.AUTHORITY_UPDATE,
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("WYO"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=ImprovementReference("IMP00002"),
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
            {
                "@id": f"{client.base_url}/capital-schemes/ATE00001",
                "reference": "ATE00001",
                "overview": {
                    "name": "Wirral Package",
                    "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                    "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                    "improvement": f"{client.base_url}/improvements/IMP00001",
                    "type": "construction",
                },
                "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z", "source": "authority update"},
            },
            {
                "@id": f"{client.base_url}/capital-schemes/ATE00002",
                "reference": "ATE00002",
                "overview": {
                    "name": "School Streets",
                    "bidSubmittingAuthority": f"{client.base_url}/authorities/LIV",
                    "fundingProgramme": f"{client.base_url}/funding-programmes/ATF3",
                    "improvement": f"{client.base_url}/improvements/IMP00001",
                    "type": "construction",
                },
                "authorityReview": None,
            },
        ]
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
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": "ATF3"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001"]


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
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF5"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": ["ATF3", "ATF4"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001", "ATE00002"]


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
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
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
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001"]


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
    authorities: AuthorityRepository,
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones1 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
    milestones1.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones1)
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones2 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00002"))
    milestones2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones2)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": "detailed design completed"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001"]


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_current_milestones(
    authorities: AuthorityRepository,
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones1 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
    milestones1.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones1)
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones2 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00002"))
    milestones2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones2)
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones3 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00003"))
    milestones3.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 4, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones3)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": ["detailed design completed", "construction started"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001", "ATE00002"]


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_no_current_milestone(
    authorities: AuthorityRepository,
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
    client: TestClient,
    access_token: str,
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    await capital_scheme_milestones.add(CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001")))
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                improvement=None,
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )
    )
    milestones2 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00002"))
    milestones2.change_milestone(
        CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
    )
    await capital_scheme_milestones.add(milestones2)

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"current-milestone": ""},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001"]


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
    assert response.json()["items"] == []


@respx.mock
def test_get_authority_bid_submitting_capital_schemes_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
