from dataclasses import dataclass
from datetime import datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.dates import is_zoned
from ate_api.domain.funding_programmes import FundingProgrammeCode


@dataclass(frozen=True)
class CapitalSchemeItemOverview:
    name: str
    funding_programme: FundingProgrammeCode


@dataclass(frozen=True)
class CapitalSchemeItemAuthorityReview:
    review_date: datetime

    def __post_init__(self) -> None:
        if self.review_date and not is_zoned(self.review_date):
            raise ValueError(f"Review date and time must include a time zone: {self.review_date}")


@dataclass(frozen=True)
class CapitalSchemeItem:
    reference: CapitalSchemeReference
    overview: CapitalSchemeItemOverview
    authority_review: CapitalSchemeItemAuthorityReview | None


class CapitalSchemeRepository:
    async def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        raise NotImplementedError()

    async def get_items_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        bid_status: BidStatus | None = None,
        current_milestones: list[Milestone | None] | None = None,
    ) -> list[CapitalSchemeItem]:
        raise NotImplementedError()

    async def update(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()
