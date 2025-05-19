from datetime import datetime, timezone

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.capital_schemes.overviews import (
    CapitalSchemeOverviewEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class TestSchemeTypeName:
    def test_from_domain(self) -> None:
        assert SchemeTypeName.from_domain(CapitalSchemeType.CONSTRUCTION) == SchemeTypeName.CONSTRUCTION

    def test_to_domain(self) -> None:
        assert SchemeTypeName.CONSTRUCTION.to_domain() == CapitalSchemeType.CONSTRUCTION


class TestCapitalSchemeOverviewEntity:
    def test_from_domain(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview, {"LIV": 1}, {"ATF3": 1}, {SchemeTypeName.CONSTRUCTION: 1}
        )

        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.bid_submitting_authority_id == 1
            and overview_entity.funding_programme_id == 1
            and overview_entity.scheme_type_id == 1
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview, {"LIV": 1}, {"ATF3": 1}, {SchemeTypeName.CONSTRUCTION: 1}
        )

        assert not overview_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview, {"LIV": 1}, {"ATF3": 1}, {SchemeTypeName.CONSTRUCTION: 1}
        )

        assert overview_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert overview_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        overview = overview_entity.to_domain()

        assert (
            overview.effective_date
            == DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 2, 1, tzinfo=timezone.utc))
            and overview.name == "Wirral Package"
            and overview.bid_submitting_authority == AuthorityAbbreviation("LIV")
            and overview.funding_programme == "ATF3"
            and overview.type == CapitalSchemeType.CONSTRUCTION
        )

    def test_to_domain_when_current(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert not overview.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
        )
