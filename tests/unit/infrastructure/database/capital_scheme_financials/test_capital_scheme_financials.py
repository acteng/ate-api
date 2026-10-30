from datetime import UTC, datetime

from ate_api.domain.capital_scheme_financials import CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database import (
    CapitalSchemeFundingEntity,
    CapitalSchemeSpendEntity,
    DataSourceEntity,
    DataSourceName,
    FundingProgrammeEntity,
)
from tests.unit.dates import local_datetime
from tests.unit.domain.builders import build_funding_programme_code


class TestCapitalSchemeFundingEntity:
    def test_from_domain(self) -> None:
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            funding_programme=FundingProgrammeCode("ATF3"),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
            surrogate_id=1,
        )

        funding_entity = CapitalSchemeFundingEntity.from_domain(
            funding, 2, {FundingProgrammeCode("ATF3"): 3}, {DataSource.ATF3_BID: 4}
        )

        assert (
            funding_entity.capital_scheme_funding_id == 1
            and funding_entity.capital_scheme_id == 2
            and funding_entity.amount == 2_000_000
            and funding_entity.funding_programme_id == 3
            and funding_entity.data_source_id == 4
            and funding_entity.effective_date_from == local_datetime(2020, 1, 1)
            and not funding_entity.effective_date_to
        )

    def test_from_domain_when_historic(self) -> None:
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            funding_programme=build_funding_programme_code(),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        funding_entity = CapitalSchemeFundingEntity.from_domain(
            funding, 0, {build_funding_programme_code(): 0}, {DataSource.ATF3_BID: 0}
        )

        assert funding_entity.effective_date_to == local_datetime(2020, 2, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            funding_programme=build_funding_programme_code(),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        funding_entity = CapitalSchemeFundingEntity.from_domain(
            funding, 0, {build_funding_programme_code(): 0}, {DataSource.ATF3_BID: 0}
        )

        assert funding_entity.effective_date_from == local_datetime(2020, 6, 1, 13)
        assert funding_entity.effective_date_to == local_datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        funding_entity = CapitalSchemeFundingEntity(
            capital_scheme_funding_id=1,
            amount=2_000_000,
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 1, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        funding = funding_entity.to_domain()

        assert funding == CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            funding_programme=FundingProgrammeCode("ATF3"),
            data_source=DataSource.ATF3_BID,
        )
        assert funding.surrogate_id == 1

    def test_to_domain_when_historic(self) -> None:
        funding_entity = CapitalSchemeFundingEntity(
            amount=2_000_000,
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 1, 1),
            effective_date_to=local_datetime(2020, 2, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        funding = funding_entity.to_domain()

        assert funding.effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        funding_entity = CapitalSchemeFundingEntity(
            amount=2_000_000,
            funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
            effective_date_from=local_datetime(2020, 6, 1, 13),
            effective_date_to=local_datetime(2020, 7, 1, 13),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        funding = funding_entity.to_domain()

        assert funding.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )


class TestCapitalSchemeSpendEntity:
    def test_from_domain(self) -> None:
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
            surrogate_id=1,
        )

        spend_entity = CapitalSchemeSpendEntity.from_domain(spend, 2, {DataSource.ATF3_BID: 3})

        assert (
            spend_entity.capital_scheme_spend_id == 1
            and spend_entity.capital_scheme_id == 2
            and spend_entity.amount == 2_000_000
            and spend_entity.effective_date_from == local_datetime(2020, 1, 1)
            and not spend_entity.effective_date_to
            and spend_entity.data_source_id == 3
        )

    def test_from_domain_when_historic(self) -> None:
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        spend_entity = CapitalSchemeSpendEntity.from_domain(spend, 0, {DataSource.ATF3_BID: 0})

        assert spend_entity.effective_date_to == local_datetime(2020, 2, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        spend_entity = CapitalSchemeSpendEntity.from_domain(spend, 0, {DataSource.ATF3_BID: 0})

        assert spend_entity.effective_date_from == local_datetime(2020, 6, 1, 13)
        assert spend_entity.effective_date_to == local_datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        spend_entity = CapitalSchemeSpendEntity(
            capital_scheme_spend_id=1,
            amount=2_000_000,
            effective_date_from=local_datetime(2020, 1, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        spend = spend_entity.to_domain()

        assert spend == CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        assert spend.surrogate_id == 1

    def test_to_domain_when_historic(self) -> None:
        spend_entity = CapitalSchemeSpendEntity(
            amount=2_000_000,
            effective_date_from=local_datetime(2020, 1, 1),
            effective_date_to=local_datetime(2020, 2, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        spend = spend_entity.to_domain()

        assert spend.effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        spend_entity = CapitalSchemeSpendEntity(
            amount=2_000_000,
            effective_date_from=local_datetime(2020, 6, 1, 13),
            effective_date_to=local_datetime(2020, 7, 1, 13),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF3_BID),
        )

        spend = spend_entity.to_domain()

        assert spend.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
