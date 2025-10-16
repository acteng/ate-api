from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money


class TestCapitalSchemeFinancial:
    @pytest.mark.parametrize(
        "effective_date_to, expected_is_open",
        [pytest.param(None, True, id="open"), pytest.param(datetime(2020, 2, 1, tzinfo=UTC), False, id="closed")],
    )
    def test_is_open(self, effective_date_to: datetime | None, expected_is_open: bool) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), effective_date_to),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        assert financial.is_open == expected_is_open

    def test_close(self) -> None:
        open_financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
            surrogate_id=1,
        )

        closed_financial = open_financial.close(datetime(2020, 2, 1, tzinfo=UTC))

        assert (
            closed_financial.effective_date
            == DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))
            and closed_financial.type == FinancialType.FUNDING_ALLOCATION
            and closed_financial.amount == Money(2_000_000)
            and closed_financial.data_source == DataSource.ATF4_BID
            and closed_financial.surrogate_id == 1
        )

    def test_cannot_close_when_closed(self) -> None:
        closed_financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        with pytest.raises(ValueError, match="Capital scheme financial is already closed"):
            closed_financial.close(datetime(2020, 2, 1, tzinfo=UTC))


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

    def test_change_financial_adds_financial(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        financials.change_financial(financial)

        assert financials.financials == [financial]

    def test_change_financial_closes_matching_current_financials(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )
        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        financials.change_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(4_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert financials.financials[0].effective_date.to == datetime(2020, 3, 1, tzinfo=UTC)
        assert financials.financials[1].effective_date.to == datetime(2020, 3, 1, tzinfo=UTC)

    def test_change_financial_preserves_other_current_financial(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financial1 = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        financials.adjust_financial(financial1)

        financials.change_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert financials.financials[0] == financial1
