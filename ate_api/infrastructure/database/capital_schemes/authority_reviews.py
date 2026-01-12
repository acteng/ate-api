from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.data_sources import DataSource
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class CapitalSchemeAuthorityReviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_authority_review"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_authority_review_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    review_date: Mapped[datetime]
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        authority_review: CapitalSchemeAuthorityReview,
        capital_scheme_id: int | None,
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_authority_review_id=authority_review.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            review_date=zoned_to_local(authority_review.review_date),
            data_source_id=data_source_ids[authority_review.data_source],
        )

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(
            review_date=local_to_zoned(self.review_date),
            data_source=self.data_source.data_source_name.to_domain(),
            surrogate_id=self.capital_scheme_authority_review_id,
        )
