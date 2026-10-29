from datetime import UTC, datetime

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money


class TestCapitalSchemeFinancials:
    def test_create(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))

        assert (
            financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and not financials.fundings
            and not financials.spend
        )

    def test_fundings_is_copy(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.adjust_funding(
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                funding_programme=FundingProgrammeCode("ATF3"),
                amount=Money(2_000_000),
                data_source=DataSource.ATF3_BID,
            )
        )

        financials.fundings.clear()

        assert financials.fundings

    def test_adjust_funding_adds_funding(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            funding_programme=FundingProgrammeCode("ATF3"),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        financials.adjust_funding(funding)

        assert financials.fundings == [funding]

    def test_adjust_funding_preserves_current_funding(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        funding1 = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            funding_programme=FundingProgrammeCode("ATF3"),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )
        financials.adjust_funding(funding1)

        financials.adjust_funding(
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                funding_programme=FundingProgrammeCode("ATF3"),
                amount=Money(1_000_000),
                data_source=DataSource.ATF3_BID,
            )
        )

        assert financials.fundings[0] == funding1

    def test_change_spend(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF3_BID,
        )

        financials.change_spend(spend)

        assert financials.spend == spend
