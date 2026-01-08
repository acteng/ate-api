from dataclasses import dataclass
from datetime import datetime

from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import is_zoned


@dataclass(frozen=True)
class CapitalSchemeAuthorityReview:
    review_date: datetime
    data_source: DataSource

    def __post_init__(self) -> None:
        if not is_zoned(self.review_date):
            raise ValueError(f"Review date and time must include a time zone: {self.review_date}")


class CapitalSchemeAuthorityReviews:
    def __init__(self, capital_scheme: CapitalSchemeReference):
        self._capital_scheme = capital_scheme
        self._authority_review: CapitalSchemeAuthorityReview | None = None

    @property
    def capital_scheme(self) -> CapitalSchemeReference:
        return self._capital_scheme

    @property
    def authority_review(self) -> CapitalSchemeAuthorityReview | None:
        return self._authority_review

    def perform_authority_review(self, authority_review: CapitalSchemeAuthorityReview) -> None:
        self._authority_review = authority_review


class CapitalSchemeAuthorityReviewsRepository:
    async def add(self, authority_reviews: CapitalSchemeAuthorityReviews) -> None:
        raise NotImplementedError()

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeAuthorityReviews | None:
        raise NotImplementedError()
