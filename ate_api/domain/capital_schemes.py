from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange


class CapitalSchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@dataclass(frozen=True)
class CapitalSchemeOverview:
    effective_date: DateTimeRange
    name: str
    bid_submitting_authority: str
    funding_programme: str
    type: CapitalSchemeType


class CapitalSchemeBidStatus(Enum):
    SUBMITTED = auto()
    FUNDED = auto()
    NOT_FUNDED = auto()
    SPLIT = auto()
    DELETED = auto()


@dataclass(frozen=True)
class CapitalSchemeBidStatusDetails:
    effective_date: DateTimeRange
    bid_status: CapitalSchemeBidStatus


@dataclass(frozen=True)
class CapitalSchemeAuthorityReview:
    review_date: datetime


class CapitalScheme:
    def __init__(
        self, reference: str, overview: CapitalSchemeOverview, bid_status_details: CapitalSchemeBidStatusDetails
    ):
        self._reference = reference
        self._overview = overview
        self._bid_status_details = bid_status_details
        self._authority_review: CapitalSchemeAuthorityReview | None = None

    @property
    def reference(self) -> str:
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

    def get(self, reference: str) -> CapitalScheme | None:
        raise NotImplementedError()

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        raise NotImplementedError()
