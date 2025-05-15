from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ate_api.domain.capital_schemes.authority_reviews import (
    CapitalSchemeAuthorityReview,
)
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class CapitalSchemeAuthorityReviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_authority_review"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_authority_review_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    review_date: Mapped[datetime]

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(review_date=zoned_to_local(authority_review.review_date))

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=local_to_zoned(self.review_date))
