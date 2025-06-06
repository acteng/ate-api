from typing import Any

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview


class CapitalSchemeReference:
    def __init__(self, reference: str):
        self._reference = reference

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CapitalSchemeReference) and self._reference == other._reference

    def __hash__(self) -> int:
        return hash(self._reference)

    def __str__(self) -> str:
        return self._reference


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
    def authority_review(self) -> CapitalSchemeAuthorityReview | None:
        return self._authority_review

    def perform_authority_review(self, authority_review: CapitalSchemeAuthorityReview) -> None:
        self._authority_review = authority_review


class CapitalSchemeRepository:
    def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        raise NotImplementedError()

    def get_references_by_bid_submitting_authority(
        self, authority_abbreviation: AuthorityAbbreviation, bid_status: BidStatus | None = None
    ) -> list[CapitalSchemeReference]:
        raise NotImplementedError()
