from dataclasses import dataclass

from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money


@dataclass(frozen=True)
class CapitalSchemeFinancial:
    effective_date: DateTimeRange
    type: FinancialType
    amount: Money
    data_source: DataSource


class CapitalSchemeFinancials:
    def __init__(self, capital_scheme: CapitalSchemeReference):
        self._capital_scheme = capital_scheme
        self._financials: list[CapitalSchemeFinancial] = []

    @property
    def capital_scheme(self) -> CapitalSchemeReference:
        return self._capital_scheme

    @property
    def financials(self) -> list[CapitalSchemeFinancial]:
        return list(self._financials)

    def change_financial(self, financial: CapitalSchemeFinancial) -> None:
        self._financials.append(financial)


class CapitalSchemeFinancialsRepository:
    async def add(self, financials: CapitalSchemeFinancials) -> None:
        raise NotImplementedError()

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        raise NotImplementedError()
