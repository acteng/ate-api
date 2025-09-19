from typing import Any

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType


class CapitalSchemeReference:
    def __init__(self, reference: str):
        self._reference = reference

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CapitalSchemeReference) and self._reference == other._reference

    def __hash__(self) -> int:
        return hash(self._reference)

    def __str__(self) -> str:
        return self._reference

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._reference)})"


class CapitalScheme:
    def __init__(
        self,
        reference: CapitalSchemeReference,
        overview: CapitalSchemeOverview,
        bid_status_details: CapitalSchemeBidStatusDetails,
    ):
        self._reference = reference
        self._overview = overview
        self._bid_status_details = bid_status_details
        self._financials: list[CapitalSchemeFinancial] = []
        self._milestones: list[CapitalSchemeMilestone] = []
        self._authority_review: CapitalSchemeAuthorityReview | None = None

    @property
    def reference(self) -> CapitalSchemeReference:
        return self._reference

    @property
    def overview(self) -> CapitalSchemeOverview:
        return self._overview

    @property
    def bid_status_details(self) -> CapitalSchemeBidStatusDetails:
        return self._bid_status_details

    @property
    def financials(self) -> list[CapitalSchemeFinancial]:
        return list(self._financials)

    def change_financial(self, financial: CapitalSchemeFinancial) -> None:
        self._financials.append(financial)

    @property
    def milestones(self) -> list[CapitalSchemeMilestone]:
        return list(self._milestones)

    @property
    def current_milestone(self) -> Milestone | None:
        actual_milestones = [
            milestone.milestone
            for milestone in self._milestones
            if milestone.observation_type == ObservationType.ACTUAL
        ]
        return sorted(actual_milestones)[-1] if actual_milestones else None

    def change_milestone(self, milestone: CapitalSchemeMilestone) -> None:
        self._milestones.append(milestone)

    @property
    def authority_review(self) -> CapitalSchemeAuthorityReview | None:
        return self._authority_review

    def perform_authority_review(self, authority_review: CapitalSchemeAuthorityReview) -> None:
        self._authority_review = authority_review


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
