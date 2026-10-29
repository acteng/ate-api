from datetime import UTC, datetime

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.moneys import Money
from ate_api.routes.capital_schemes.financials import (
    CapitalSchemeFinancialsModel,
    CapitalSchemeFundingModel,
    CapitalSchemeSpendModel,
)
from ate_api.routes.collections import CollectionModel
from ate_api.routes.data_sources import DataSourceModel


class TestCapitalSchemeFundingModel:
    def test_from_domain(self) -> None:
        funding = CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        funding_model = CapitalSchemeFundingModel.from_domain(funding)

        assert funding_model == CapitalSchemeFundingModel(amount=2_000_000, source=DataSourceModel.ATF4_BID)

    def test_to_domain(self) -> None:
        funding_model = CapitalSchemeFundingModel(amount=2_000_000, source=DataSourceModel.ATF4_BID)

        funding = funding_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert funding == CapitalSchemeFunding(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )


class TestCapitalSchemeSpendModel:
    def test_from_domain(self) -> None:
        spend = CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(1_000_000),
            data_source=DataSource.ATF4_BID,
        )

        spend_model = CapitalSchemeSpendModel.from_domain(spend)

        assert spend_model == CapitalSchemeSpendModel(amount=1_000_000, source=DataSourceModel.ATF4_BID)

    def test_to_domain(self) -> None:
        spend_model = CapitalSchemeSpendModel(amount=1_000_000, source=DataSourceModel.ATF4_BID)

        spend = spend_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert spend == CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            amount=Money(1_000_000),
            data_source=DataSource.ATF4_BID,
        )


class TestCapitalSchemeFinancialsModel:
    def test_from_domain(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.adjust_funding(
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )
        financials.change_spend(
            CapitalSchemeSpend(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        financials_model = CapitalSchemeFinancialsModel.from_domain(financials)

        assert financials_model == CapitalSchemeFinancialsModel(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[CapitalSchemeFundingModel(amount=2_000_000, source=DataSourceModel.ATF4_BID)]
            ),
            spend=CapitalSchemeSpendModel(amount=1_000_000, source=DataSourceModel.ATF4_BID),
        )

    def test_from_domain_when_no_spend(self) -> None:
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))

        financials_model = CapitalSchemeFinancialsModel.from_domain(financials)

        assert not financials_model.spend
