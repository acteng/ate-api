from datetime import UTC, datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.infrastructure.database import AuthorityEntity, DataSourceEntity, DataSourceName, ImprovementOverviewEntity


class TestImprovementOverviewEntity:
    def test_from_domain(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_entity = ImprovementOverviewEntity.from_domain(
            overview,
            {AuthorityAbbreviation("LIV"): 1},
            {DataSource.AUTHORITY_UPDATE: 2},
        )

        assert (
            overview_entity.improvement_name == "Wirral Package"
            and overview_entity.improvement_description is None
            and overview_entity.funding_managed_by_id == 1
            and overview_entity.data_source_id == 2
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_sets_description(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_entity = ImprovementOverviewEntity.from_domain(
            overview,
            {AuthorityAbbreviation("LIV"): 0},
            {DataSource.AUTHORITY_UPDATE: 0},
        )

        assert (
            overview_entity.improvement_description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
        )

    def test_from_domain_when_current(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_entity = ImprovementOverviewEntity.from_domain(
            overview,
            {AuthorityAbbreviation("LIV"): 0},
            {DataSource.AUTHORITY_UPDATE: 0},
        )

        assert not overview_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_entity = ImprovementOverviewEntity.from_domain(
            overview,
            {AuthorityAbbreviation("LIV"): 0},
            {DataSource.AUTHORITY_UPDATE: 0},
        )

        assert overview_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert overview_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        overview_entity = ImprovementOverviewEntity(
            improvement_name="Wirral Package",
            funding_managed_by=AuthorityEntity(authority_abbreviation="LIV"),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        overview = overview_entity.to_domain()

        assert (
            overview.effective_date == DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))
            and overview.name == "Wirral Package"
            and overview.description is None
            and overview.funding_managed_by == AuthorityAbbreviation("LIV")
            and overview.data_source == DataSource.AUTHORITY_UPDATE
        )

    def test_to_domain_sets_description(self) -> None:
        overview_entity = ImprovementOverviewEntity(
            improvement_name="Wirral Package",
            improvement_description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AuthorityEntity(authority_abbreviation="LIV"),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
            effective_date_from=datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert (
            overview.description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
        )

    def test_to_domain_when_current(self) -> None:
        overview_entity = ImprovementOverviewEntity(
            improvement_name="Wirral Package",
            funding_managed_by=AuthorityEntity(authority_abbreviation="LIV"),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
            effective_date_from=datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert not overview.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        overview_entity = ImprovementOverviewEntity(
            improvement_name="Wirral Package",
            funding_managed_by=AuthorityEntity(authority_abbreviation="LIV"),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
