from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Self

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
    surrogate_id: int | None = field(default=None, repr=False, compare=False)

    @property
    def is_open(self) -> bool:
        return self.effective_date.is_open

    def close(self, effective_date_to: datetime) -> Self:
        if not self.is_open:
            raise ValueError("Capital scheme financial is already closed")

        return replace(self, effective_date=self.effective_date.close(effective_date_to))


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

    def adjust_financial(self, financial: CapitalSchemeFinancial) -> None:
        self._financials.append(financial)

    def change_financial(self, financial: CapitalSchemeFinancial) -> None:
        # funding allocation is represented by a series of adjustments that should not be closed
        if financial.type == FinancialType.FUNDING_ALLOCATION:
            raise ValueError("Funding allocation cannot be changed")

        self._financials = list(
            map(
                lambda f: f.close(financial.effective_date.from_) if f.is_open and self._matches(f, financial) else f,
                self._financials,
            )
        )
        self._financials.append(financial)

    @staticmethod
    def _matches(financial1: CapitalSchemeFinancial, financial2: CapitalSchemeFinancial) -> bool:
        return financial1.type == financial2.type


class CapitalSchemeFinancialsRepository:
    async def add(self, financials: CapitalSchemeFinancials) -> None:
        raise NotImplementedError()

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        raise NotImplementedError()

    async def update(self, financials: CapitalSchemeFinancials) -> None:
        raise NotImplementedError()
