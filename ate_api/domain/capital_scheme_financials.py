from dataclasses import dataclass, field

from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money


@dataclass(frozen=True)
class CapitalSchemeFunding:
    effective_date: DateTimeRange
    funding_programme: FundingProgrammeCode
    amount: Money
    data_source: DataSource
    surrogate_id: int | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class CapitalSchemeSpend:
    effective_date: DateTimeRange
    amount: Money
    data_source: DataSource
    surrogate_id: int | None = field(default=None, repr=False, compare=False)


class CapitalSchemeFinancials:
    def __init__(self, capital_scheme: CapitalSchemeReference):
        self._capital_scheme = capital_scheme
        self._fundings: list[CapitalSchemeFunding] = []
        self._spend: CapitalSchemeSpend | None = None

    @property
    def capital_scheme(self) -> CapitalSchemeReference:
        return self._capital_scheme

    @property
    def fundings(self) -> list[CapitalSchemeFunding]:
        return list(self._fundings)

    def adjust_funding(self, funding: CapitalSchemeFunding) -> None:
        self._fundings.append(funding)

    @property
    def spend(self) -> CapitalSchemeSpend | None:
        return self._spend

    def change_spend(self, spend: CapitalSchemeSpend) -> None:
        self._spend = spend


class CapitalSchemeFinancialsRepository:
    async def add(self, financials: CapitalSchemeFinancials) -> None:
        raise NotImplementedError()

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        raise NotImplementedError()

    async def update(self, financials: CapitalSchemeFinancials) -> None:
        raise NotImplementedError()
