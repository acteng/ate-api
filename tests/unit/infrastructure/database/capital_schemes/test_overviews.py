from datetime import UTC, datetime

import pytest

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import ImprovementReference
from ate_api.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
    ImprovementEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)
from tests.unit.dates import local_datetime
from tests.unit.domain.builders import (
    build_authority_abbreviation,
    build_capital_scheme_overview,
    build_capital_scheme_type,
    build_funding_programme_code,
)
from tests.unit.infrastructure.database.builders import build_improvement_overview_entity


@pytest.mark.parametrize(
    "type_, type_name",
    [
        (CapitalSchemeType.DEVELOPMENT, SchemeTypeName.DEVELOPMENT),
        (CapitalSchemeType.CONSTRUCTION, SchemeTypeName.CONSTRUCTION),
    ],
)
class TestSchemeTypeName:
    def test_from_domain(self, type_: CapitalSchemeType, type_name: SchemeTypeName) -> None:
        assert SchemeTypeName.from_domain(type_) == type_name

    def test_to_domain(self, type_: CapitalSchemeType, type_name: SchemeTypeName) -> None:
        assert type_name.to_domain() == type_


class TestCapitalSchemeOverviewEntity:
    def test_from_domain(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview,
            {AuthorityAbbreviation("LIV"): 1},
            {FundingProgrammeCode("ATF3"): 2},
            {ImprovementReference("IMP00001"): 3},
            {CapitalSchemeType.CONSTRUCTION: 4},
        )

        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.bid_submitting_authority_id == 1
            and overview_entity.funding_programme_id == 2
            and overview_entity.improvement_id == 3
            and overview_entity.scheme_type_id == 4
            and overview_entity.effective_date_from == local_datetime(2020, 1, 1)
            and not overview_entity.effective_date_to
        )

    def test_from_domain_without_improvement(self) -> None:
        overview = build_capital_scheme_overview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), improvement=None
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview,
            {build_authority_abbreviation(): 0},
            {build_funding_programme_code(): 0},
            {},
            {build_capital_scheme_type(): 0},
        )

        assert overview_entity.improvement_id is None

    def test_from_domain_when_historic(self) -> None:
        overview = build_capital_scheme_overview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview,
            {build_authority_abbreviation(): 0},
            {build_funding_programme_code(): 0},
            {},
            {build_capital_scheme_type(): 0},
        )

        assert overview_entity.effective_date_to == local_datetime(2020, 2, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        overview = build_capital_scheme_overview(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC))
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview,
            {build_authority_abbreviation(): 0},
            {build_funding_programme_code(): 0},
            {},
            {build_capital_scheme_type(): 0},
        )

        assert overview_entity.effective_date_from == local_datetime(2020, 6, 1, 13)
        assert overview_entity.effective_date_to == local_datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            improvement=ImprovementEntity(
                improvement_reference="IMP00001", improvement_overviews=[build_improvement_overview_entity()]
            ),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=local_datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert (
            overview.effective_date == DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC))
            and overview.name == "Wirral Package"
            and overview.bid_submitting_authority == AuthorityAbbreviation("LIV")
            and overview.funding_programme == FundingProgrammeCode("ATF3")
            and overview.improvement == ImprovementReference("IMP00001")
            and overview.type == CapitalSchemeType.CONSTRUCTION
        )

    def test_to_domain_without_improvement(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=local_datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert overview.improvement is None

    def test_to_domain_when_historic(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=local_datetime(2020, 1, 1),
            effective_date_to=local_datetime(2020, 2, 1),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=local_datetime(2020, 6, 1, 13),
            effective_date_to=local_datetime(2020, 7, 1, 13),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
