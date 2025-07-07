from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.milestones import Milestone, MilestoneRepository
from ate_api.domain.funding_programmes import FundingProgrammeCode


class MemoryCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self) -> None:
        self._capital_schemes: dict[CapitalSchemeReference, CapitalScheme] = {}

    async def add(self, capital_scheme: CapitalScheme) -> None:
        self._capital_schemes[capital_scheme.reference] = capital_scheme

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        return self._capital_schemes.get(reference)

    async def get_references_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        bid_status: BidStatus | None = None,
        current_milestones: list[Milestone] | None = None,
    ) -> list[CapitalSchemeReference]:
        return sorted(
            [
                reference
                for reference, capital_scheme in self._capital_schemes.items()
                if capital_scheme.overview.bid_submitting_authority == authority_abbreviation
                and (
                    not funding_programme_codes or capital_scheme.overview.funding_programme in funding_programme_codes
                )
                and (not bid_status or capital_scheme.bid_status_details.bid_status == bid_status)
                and (not current_milestones or capital_scheme.current_milestone in current_milestones)
            ],
            key=lambda reference: str(reference),
        )


class MemoryMilestoneRepository(MilestoneRepository):
    async def get_all(self) -> list[Milestone]:
        return list(Milestone)
