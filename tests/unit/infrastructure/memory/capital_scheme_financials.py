from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFinancialsRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference


class MemoryCapitalSchemeFinancialsRepository(CapitalSchemeFinancialsRepository):
    def __init__(self) -> None:
        self._financials: dict[CapitalSchemeReference, CapitalSchemeFinancials] = {}

    async def add(self, financials: CapitalSchemeFinancials) -> None:
        self._financials[financials.capital_scheme] = financials

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        return self._financials.get(capital_scheme)
