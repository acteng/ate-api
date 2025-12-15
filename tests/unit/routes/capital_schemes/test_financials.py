from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.routes.capital_schemes.financials import (
    CapitalSchemeFinancialModel,
    CapitalSchemeFinancialsModel,
    CreateCapitalSchemeFinancialModel,
)
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
            type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000, source=DataSourceModel.ATF4_BID
        )

    def test_to_domain(self) -> None:
        financial_model = CapitalSchemeFinancialModel(
            type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000, source=DataSourceModel.ATF4_BID
        )

        financial = financial_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert financial == CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )


class TestCreateCapitalSchemeFinancialModel:
    @pytest.mark.parametrize(
        "type_",
        (
            FinancialTypeModel.EXPECTED_COST,
            FinancialTypeModel.ACTUAL_COST,
            FinancialTypeModel.SPEND_TO_DATE,
            FinancialTypeModel.FUNDING_REQUEST,
        ),
    )
    def test_can_create_with_financial_type(self, type_: FinancialTypeModel) -> None:
        financial_model = CreateCapitalSchemeFinancialModel(type=type_, amount=0, source=DataSourceModel.PULSE_5)

        assert financial_model

    def test_cannot_create_with_funding_allocation(self) -> None:
        with pytest.raises(ValidationError) as exception_info:
            CreateCapitalSchemeFinancialModel(
                type=FinancialTypeModel.FUNDING_ALLOCATION, amount=0, source=DataSourceModel.PULSE_5
            )

        assert exception_info.value.errors() == [
            {
                "input": FinancialTypeModel.FUNDING_ALLOCATION,
                "loc": ("type",),
                "msg": "Funding allocation cannot be created",
                "type": "enum",
            }
        ]


class TestCapitalSchemeFinancialsModel:
    def test_from_domain(self) -> None:
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
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )

        financials_model = CapitalSchemeFinancialsModel.from_domain(financials)

        assert financials_model.items == [
            CapitalSchemeFinancialModel(
                type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000, source=DataSourceModel.ATF4_BID
            ),
            CapitalSchemeFinancialModel(
                type=FinancialTypeModel.SPEND_TO_DATE, amount=1_000_000, source=DataSourceModel.ATF4_BID
            ),
        ]
