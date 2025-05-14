from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeRepository,
)
from ate_api.domain.funding_programmes import (
    FundingProgramme,
    FundingProgrammeRepository,
)


class MemoryFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self) -> None:
        self._funding_programmes: dict[str, FundingProgramme] = {}

    def add(self, funding_programme: FundingProgramme) -> None:
        self._funding_programmes[funding_programme.code] = funding_programme

    def get(self, code: str) -> FundingProgramme | None:
        return self._funding_programmes.get(code)


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: dict[str, Authority] = {}

    def add(self, authority: Authority) -> None:
        self._authorities[authority.abbreviation] = authority

    def get(self, abbreviation: str) -> Authority | None:
        return self._authorities.get(abbreviation)


class MemoryCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self) -> None:
        self._capital_schemes: dict[str, CapitalScheme] = {}

    def add(self, capital_scheme: CapitalScheme) -> None:
        self._capital_schemes[capital_scheme.reference] = capital_scheme

    def get(self, reference: str) -> CapitalScheme | None:
        return self._capital_schemes.get(reference)

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        return sorted(
            reference
            for reference, capital_scheme in self._capital_schemes.items()
            if capital_scheme.overview.bid_submitting_authority == authority_abbreviation
        )
