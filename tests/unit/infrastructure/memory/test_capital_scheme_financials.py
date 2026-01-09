from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from tests.unit.infrastructure.memory.capital_scheme_financials import MemoryCapitalSchemeFinancialsRepository


class TestMemoryCapitalSchemeFinancialsRepository:
    @pytest.fixture(name="capital_scheme_financials")
    def capital_scheme_financials_fixture(self) -> MemoryCapitalSchemeFinancialsRepository:
        return MemoryCapitalSchemeFinancialsRepository()

    async def test_add(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial1 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial1)
        financial2 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.SPEND_TO_DATE,
            amount=Money(1_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial2)

        await capital_scheme_financials.add(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
        assert (
            actual_financials
            and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_financials.financials == [financial1, financial2]
        )

    async def test_get(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial1 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial1)
        financial2 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.SPEND_TO_DATE,
            amount=Money(1_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial2)
        await capital_scheme_financials.add(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert (
            actual_financials
            and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_financials.financials == [financial1, financial2]
        )

    async def test_get_when_not_found(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert not financials

    async def test_update(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.change_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(3_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )
        await capital_scheme_financials.add(financials)
        financial2 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
            type=FinancialType.SPEND_TO_DATE,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.change_financial(financial2)

        await capital_scheme_financials.update(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
        assert actual_financials and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
        actual_financial1, actual_financial2 = actual_financials.financials
        assert actual_financial1.effective_date.to == datetime(2020, 3, 1, tzinfo=UTC)
        assert actual_financial2 == financial2
