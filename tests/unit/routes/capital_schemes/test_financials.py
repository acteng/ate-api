from datetime import UTC, datetime

from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.routes.capital_schemes.financials import CapitalSchemeFinancialModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.financial_types import FinancialTypeModel


class TestCapitalSchemeFinancialModel:
    def test_from_domain(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        financial_model = CapitalSchemeFinancialModel.from_domain(financial)

        assert financial_model == CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION,
            amount=2_000_000,
            source=DataSourceModel.ATF4_BID,
        )

    def test_to_domain(self) -> None:
        financial_model = CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION,
            amount=2_000_000,
            source=DataSourceModel.ATF4_BID,
        )

        financial = financial_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert financial == CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
