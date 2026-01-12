from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.funding_programmes import FundingProgrammeCode


class CapitalSchemeRepository:
    async def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        raise NotImplementedError()

    async def get_references_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        bid_status: BidStatus | None = None,
        current_milestones: list[Milestone | None] | None = None,
    ) -> list[CapitalSchemeReference]:
        raise NotImplementedError()

    async def update(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()
