from datetime import datetime
from typing import Self

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.routes.base import BaseModel


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(review_date=authority_review.review_date)

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=self.review_date)
