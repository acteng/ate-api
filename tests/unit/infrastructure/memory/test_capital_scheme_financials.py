from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.moneys import Money
from tests.unit.infrastructure.memory.capital_scheme_financials import MemoryCapitalSchemeFinancialsRepository


class TestMemoryCapitalSchemeFinancialsRepository:
    @pytest.fixture(name="capital_scheme_financials")
    def capital_scheme_financials_fixture(self) -> MemoryCapitalSchemeFinancialsRepository:
        return MemoryCapitalSchemeFinancialsRepository()

    async def test_add(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.adjust_funding(funding)
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(1_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.change_spend(spend)

        await capital_scheme_financials.add(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
        assert (
            actual_financials
            and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_financials.fundings == [funding]
            and actual_financials.spend == spend
        )

    async def test_get(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.adjust_funding(funding)
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(1_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.change_spend(spend)
        await capital_scheme_financials.add(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert (
            actual_financials
            and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_financials.fundings == [funding]
            and actual_financials.spend == spend
        )

    async def test_get_when_not_found(self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository) -> None:
        financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert not financials

    async def test_update_updates_funding(
        self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository
    ) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        funding1 = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(3_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.adjust_funding(funding1)
        await capital_scheme_financials.add(financials)
        funding2 = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.adjust_funding(funding2)

        await capital_scheme_financials.update(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
        assert actual_financials and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
        assert actual_financials.fundings == [funding1, funding2]

    async def test_update_updates_spend(
        self, capital_scheme_financials: MemoryCapitalSchemeFinancialsRepository
    ) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.change_spend(
            CapitalSchemeSpend(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                amount=Money(3_000_000),
                data_source=DataSource.ATF3_BID,
            )
        )
        await capital_scheme_financials.add(financials)
        spend2 = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.change_spend(spend2)

        await capital_scheme_financials.update(financials)

        actual_financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
        assert actual_financials and actual_financials.capital_scheme == CapitalSchemeReference("ATE00001")
        assert actual_financials.spend == spend2
