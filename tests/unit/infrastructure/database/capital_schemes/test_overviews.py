from datetime import UTC, datetime

from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import ImprovementReference
from ate_api.infrastructure.database import CapitalSchemeOverviewEntity, FundingProgrammeEntity
from tests.unit.dates import local_datetime
from tests.unit.domain.builders import build_capital_scheme_overview, build_funding_programme_code
from tests.unit.infrastructure.database.builders import EntityBuilder


class TestCapitalSchemeOverviewEntity:
    def test_from_domain(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(
            overview, {FundingProgrammeCode("ATF3"): 2}, {ImprovementReference("IMP00001"): 3}
        )

        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.funding_programme_id == 2
            and overview_entity.improvement_id == 3
            and overview_entity.effective_date_from == local_datetime(2020, 1, 1)
            and not overview_entity.effective_date_to
        )

    def test_from_domain_without_improvement(self) -> None:
        overview = build_capital_scheme_overview(improvement=None)

        overview_entity = CapitalSchemeOverviewEntity.from_domain(overview, {build_funding_programme_code(): 0}, {})

        assert overview_entity.improvement_id is None

    def test_from_domain_when_historic(self) -> None:
        overview = build_capital_scheme_overview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(overview, {build_funding_programme_code(): 0}, {})

        assert overview_entity.effective_date_to == local_datetime(2020, 2, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        overview = build_capital_scheme_overview(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC))
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(overview, {build_funding_programme_code(): 0}, {})

        assert overview_entity.effective_date_from == local_datetime(2020, 6, 1, 13)
        assert overview_entity.effective_date_to == local_datetime(2020, 7, 1, 13)

    def test_to_domain(self, entities: EntityBuilder) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            improvement=entities.build_improvement(reference="IMP00001"),
            effective_date_from=local_datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert (
            overview.effective_date == DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC))
            and overview.name == "Wirral Package"
            and overview.funding_programme == FundingProgrammeCode("ATF3")
            and overview.improvement == ImprovementReference("IMP00001")
        )

    def test_to_domain_without_improvement(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 1, 1),
        )

        overview = overview_entity.to_domain()

        assert overview.improvement is None

    def test_to_domain_when_historic(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 1, 1),
            effective_date_to=local_datetime(2020, 2, 1),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            scheme_name="Wirral Package",
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 6, 1, 13),
            effective_date_to=local_datetime(2020, 7, 1, 13),
        )

        overview = overview_entity.to_domain()

        assert overview.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
