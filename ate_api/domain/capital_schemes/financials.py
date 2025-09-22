from dataclasses import dataclass

from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money


@dataclass(frozen=True)
class CapitalSchemeFinancial:
    effective_date: DateTimeRange
    type: FinancialType
    amount: Money
