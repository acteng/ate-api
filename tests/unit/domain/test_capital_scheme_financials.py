from datetime import UTC, datetime

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money


class TestCapitalSchemeFinancials:
    def test_create(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))

        assert financials.capital_scheme == CapitalSchemeReference("ATE00001") and not financials.financials

    def test_financials_is_copy(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        financials.financials.clear()

        assert financials.financials

    def test_adjust_financial_adds_financial(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        financials.adjust_financial(financial)

        assert financials.financials == [financial]

    def test_adjust_financial_preserves_current_financial(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial1 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial1)

        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert financials.financials[0] == financial1
