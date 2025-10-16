from datetime import UTC, datetime

from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database import CapitalSchemeFinancialEntity, FinancialTypeEntity, FinancialTypeName


class TestCapitalSchemeFinancialEntity:
    def test_from_domain(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(financial, {FinancialType.FUNDING_ALLOCATION: 1})

        assert (
            financial_entity.financial_type_id == 1
            and financial_entity.amount == 2_000_000
            and financial_entity.effective_date_from == datetime(2020, 1, 1)
            and financial_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(financial, {FinancialType.FUNDING_ALLOCATION: 0})

        assert not financial_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(financial, {FinancialType.FUNDING_ALLOCATION: 0})

        assert financial_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert financial_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        financial = financial_entity.to_domain()

        assert financial == CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
        )

    def test_to_domain_when_current(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 1, 1),
        )

        financial = financial_entity.to_domain()

        assert not financial.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        financial = financial_entity.to_domain()

        assert financial.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
