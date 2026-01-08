from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey, Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, aliased, joinedload, mapped_column, relationship

from ate_api.domain.capital_scheme_authority_reviews import (
    CapitalSchemeAuthorityReview,
    CapitalSchemeAuthorityReviews,
    CapitalSchemeAuthorityReviewsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.capital_schemes.capital_schemes import CapitalSchemeEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity, DataSourceName
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
        capital_scheme_id: int,
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_id=capital_scheme_id,
            review_date=zoned_to_local(authority_review.review_date),
            data_source_id=data_source_ids[authority_review.data_source],
        )

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(
            review_date=local_to_zoned(self.review_date), data_source=self.data_source.data_source_name.to_domain()
        )


class DatabaseCapitalSchemeAuthorityReviewsRepository(CapitalSchemeAuthorityReviewsRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, authority_reviews: CapitalSchemeAuthorityReviews) -> None:
        if not authority_reviews.authority_review:
            return

        capital_scheme_id = await self._get_capital_scheme_id(authority_reviews)
        data_source_ids = await self._get_data_source_ids(authority_reviews)

        self._session.add(
            CapitalSchemeAuthorityReviewEntity.from_domain(
                authority_reviews.authority_review, capital_scheme_id, data_source_ids
            )
        )

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeAuthorityReviews | None:
        ranked_capital_scheme_authority_reviews = self._select_ranked_capital_scheme_authority_reviews().cte()
        ranked_capital_scheme_authority_reviews_alias = aliased(
            CapitalSchemeAuthorityReviewEntity,
            ranked_capital_scheme_authority_reviews,
            name="CapitalSchemeAuthorityReviewEntity",
        )

        result = await self._session.execute(
            select(CapitalSchemeEntity, ranked_capital_scheme_authority_reviews_alias)
            .options(joinedload(ranked_capital_scheme_authority_reviews_alias.data_source))
            .outerjoin(
                ranked_capital_scheme_authority_reviews_alias,
                and_(
                    CapitalSchemeEntity.capital_scheme_id
                    == ranked_capital_scheme_authority_reviews_alias.capital_scheme_id,
                    ranked_capital_scheme_authority_reviews.c.rank == 1,
                ),
            )
            .where(CapitalSchemeEntity.scheme_reference == str(capital_scheme))
        )
        row = result.one_or_none()

        if not row:
            return None

        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=capital_scheme)
        if row.CapitalSchemeAuthorityReviewEntity:
            authority_reviews.perform_authority_review(row.CapitalSchemeAuthorityReviewEntity.to_domain())
        return authority_reviews

    async def _get_capital_scheme_id(self, authority_reviews: CapitalSchemeAuthorityReviews) -> int:
        capital_scheme_reference = str(authority_reviews.capital_scheme)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_data_source_ids(self, authority_reviews: CapitalSchemeAuthorityReviews) -> dict[DataSource, int]:
        if not authority_reviews.authority_review:
            return {}

        data_source_name = DataSourceName.from_domain(authority_reviews.authority_review.data_source)
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name == data_source_name
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}

    @staticmethod
    def _select_ranked_capital_scheme_authority_reviews() -> Select[tuple[CapitalSchemeAuthorityReviewEntity, int]]:
        return select(
            CapitalSchemeAuthorityReviewEntity,
            func.rank()
            .over(
                partition_by=CapitalSchemeAuthorityReviewEntity.capital_scheme_id,
                order_by=CapitalSchemeAuthorityReviewEntity.review_date.desc(),
            )
            .label("rank"),
        )
