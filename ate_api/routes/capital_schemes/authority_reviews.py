from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from ate_api.clock import get_clock
from ate_api.database import get_session
from ate_api.domain.capital_scheme_authority_reviews import (
    CapitalSchemeAuthorityReview,
    CapitalSchemeAuthorityReviewsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.infrastructure.clock import Clock
from ate_api.repositories import get_capital_scheme_authority_reviews_repository
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


class CreateCapitalSchemeAuthorityReviewModel(BaseModel):
    source: DataSourceModel

    def to_domain(self, now: datetime) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=now, data_source=self.source.to_domain())


router = APIRouter()


@router.post(
    "/{reference}/authority-reviews",
    status_code=HTTP_201_CREATED,
    summary="Create capital scheme authority review",
    responses={HTTP_404_NOT_FOUND: {}},
)
async def create_authority_review(
    clock: Annotated[Clock, Depends(get_clock)],
    capital_scheme_authority_reviews: Annotated[
        CapitalSchemeAuthorityReviewsRepository, Depends(get_capital_scheme_authority_reviews_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
    reference: str,
    authority_review_model: CreateCapitalSchemeAuthorityReviewModel,
) -> CapitalSchemeAuthorityReviewModel:
    """
    Creates an authority review for a capital scheme.
    """
    authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference(reference))

    if not authority_reviews:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    authority_review = authority_review_model.to_domain(clock.now)
    authority_reviews.perform_authority_review(authority_review)
    await capital_scheme_authority_reviews.update(authority_reviews)
    await session.commit()

    return CapitalSchemeAuthorityReviewModel.from_domain(authority_review)
