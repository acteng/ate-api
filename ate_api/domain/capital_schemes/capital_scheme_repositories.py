from dataclasses import dataclass

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.capital_schemes.statuses import Status
from ate_api.domain.funding_programmes import FundingProgrammeCode


@dataclass(frozen=True)
class CapitalSchemeItem:
    reference: CapitalSchemeReference
    overview: CapitalSchemeOverview
    authority_review: CapitalSchemeAuthorityReview | None


class CapitalSchemeRepository:
    async def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        raise NotImplementedError()

    async def get_items_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        status: Status | None = None,
    ) -> list[CapitalSchemeItem]:
        raise NotImplementedError()

    async def update(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()
