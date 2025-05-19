from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository


class MemoryFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self) -> None:
        self._funding_programmes: dict[FundingProgrammeCode, FundingProgramme] = {}

    def add(self, funding_programme: FundingProgramme) -> None:
        self._funding_programmes[funding_programme.code] = funding_programme

    def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        return self._funding_programmes.get(code)


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: dict[AuthorityAbbreviation, Authority] = {}

    def add(self, authority: Authority) -> None:
        self._authorities[authority.abbreviation] = authority

    def get(self, abbreviation: AuthorityAbbreviation) -> Authority | None:
        return self._authorities.get(abbreviation)


class MemoryCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self) -> None:
        self._capital_schemes: dict[CapitalSchemeReference, CapitalScheme] = {}

    def add(self, capital_scheme: CapitalScheme) -> None:
        self._capital_schemes[capital_scheme.reference] = capital_scheme

    def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        return self._capital_schemes.get(reference)

    def get_references_by_bid_submitting_authority(
        self, authority_abbreviation: AuthorityAbbreviation, bid_status: CapitalSchemeBidStatus | None = None
    ) -> list[CapitalSchemeReference]:
        return sorted(
            [
                reference
                for reference, capital_scheme in self._capital_schemes.items()
                if capital_scheme.overview.bid_submitting_authority == authority_abbreviation
                and (not bid_status or capital_scheme.bid_status_details.bid_status == bid_status)
            ],
            key=lambda reference: str(reference),
        )
