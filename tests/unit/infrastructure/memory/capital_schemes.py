from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestonesRepository, Milestone
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_scheme_repositories import (
    CapitalSchemeItem,
    CapitalSchemeItemOverview,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.funding_programmes import FundingProgrammeCode


class MemoryCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, capital_scheme_milestones: CapitalSchemeMilestonesRepository) -> None:
        self._capital_scheme_milestones = capital_scheme_milestones
        self._capital_schemes: dict[CapitalSchemeReference, CapitalScheme] = {}

    async def add(self, capital_scheme: CapitalScheme) -> None:
        self._capital_schemes[capital_scheme.reference] = capital_scheme

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        return self._capital_schemes.get(reference)

    async def get_items_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        bid_status: BidStatus | None = None,
        current_milestones: list[Milestone | None] | None = None,
    ) -> list[CapitalSchemeItem]:
        return sorted(
            [
                self._to_item(capital_scheme)
                for reference, capital_scheme in self._capital_schemes.items()
                if capital_scheme.overview.bid_submitting_authority == authority_abbreviation
                and (
                    not funding_programme_codes or capital_scheme.overview.funding_programme in funding_programme_codes
                )
                and (not bid_status or capital_scheme.bid_status_details.bid_status == bid_status)
                and (not current_milestones or (await self._get_current_milestone(reference)) in current_milestones)
            ],
            key=lambda capital_scheme_item: str(capital_scheme_item.reference),
        )

    async def update(self, capital_scheme: CapitalScheme) -> None:
        self._capital_schemes[capital_scheme.reference] = capital_scheme

    @staticmethod
    def _to_item(capital_scheme: CapitalScheme) -> CapitalSchemeItem:
        return CapitalSchemeItem(
            reference=capital_scheme.reference,
            overview=CapitalSchemeItemOverview(
                name=capital_scheme.overview.name, funding_programme=capital_scheme.overview.funding_programme
            ),
            authority_review=capital_scheme.authority_review,
        )

    async def _get_current_milestone(self, capital_scheme: CapitalSchemeReference) -> Milestone | None:
        milestones = await self._capital_scheme_milestones.get(capital_scheme)
        assert milestones
        return milestones.current_milestone
