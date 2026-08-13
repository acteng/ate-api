from datetime import UTC, datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from ate_api.domain.improvements.overviews import ImprovementOverview
from tests.unit.domain.builders import build_authority, build_capital_scheme, build_capital_scheme_overview


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
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))
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
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("WYO")))
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
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
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
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))
    await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF5")))
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF4"),
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF5"),
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
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"funding-programme-code": "foo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filters_by_status(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
            ),
            status=CapitalSchemeStatus(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
            ),
        )
    )
    await capital_schemes.add(
        build_capital_scheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=build_capital_scheme_overview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
            ),
            status=CapitalSchemeStatus(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.PIPELINE
            ),
        )
    )

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"status": "active"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert [item["reference"] for item in response.json()["items"]] == ["ATE00001"]


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_filter_by_unknown_status(
    authorities: AuthorityRepository, capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))

    response = client.get(
        "/authorities/LIV/capital-schemes/bid-submitting",
        params={"status": "foo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 422


@respx.mock
async def test_get_authority_bid_submitting_capital_schemes_when_none(
    authorities: AuthorityRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(build_authority(abbreviation=AuthorityAbbreviation("LIV")))

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
