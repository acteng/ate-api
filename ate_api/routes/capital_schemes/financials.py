from datetime import datetime
from typing import Self

from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.moneys import Money
from ate_api.routes.base import BaseModel
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
