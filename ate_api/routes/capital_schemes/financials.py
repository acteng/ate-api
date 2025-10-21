from datetime import datetime
from typing import Self

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.moneys import Money
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.financial_types import FinancialTypeModel


class CapitalSchemeFinancialModel(BaseModel):
    type: FinancialTypeModel
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, financial: CapitalSchemeFinancial) -> Self:
        return cls(
            type=FinancialTypeModel.from_domain(financial.type),
            amount=financial.amount.amount,
            source=DataSourceModel.from_domain(financial.data_source),
        )

    def to_domain(self, now: datetime) -> CapitalSchemeFinancial:
        return CapitalSchemeFinancial(
            effective_date=DateTimeRange(now),
            type=self.type.to_domain(),
            amount=Money(self.amount),
            data_source=self.source.to_domain(),
        )


class CapitalSchemeFinancialsModel(CollectionModel[CapitalSchemeFinancialModel]):
    @classmethod
    def from_domain(cls, financials: CapitalSchemeFinancials) -> Self:
        return cls(items=[CapitalSchemeFinancialModel.from_domain(financial) for financial in financials.financials])

    def to_domain(self, capital_scheme: CapitalSchemeReference, now: datetime) -> CapitalSchemeFinancials:
        financials = CapitalSchemeFinancials(capital_scheme=capital_scheme)
        for financial in self.items:
            financials.adjust_financial(financial.to_domain(now))
        return financials
