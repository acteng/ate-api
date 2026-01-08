from datetime import datetime
from typing import Self

from ate_api.domain.capital_scheme_authority_reviews import CapitalSchemeAuthorityReview
from ate_api.routes.base import BaseModel
from ate_api.routes.data_sources import DataSourceModel


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime
    source: DataSourceModel

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(
            review_date=authority_review.review_date, source=DataSourceModel.from_domain(authority_review.data_source)
        )

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=self.review_date, data_source=self.source.to_domain())
