from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import ConfigDict
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from ate_api.clock import get_clock
from ate_api.database import get_unit_of_work
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.infrastructure.clock import Clock
from ate_api.repositories import get_capital_scheme_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.unit_of_work import UnitOfWork


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime
    source: DataSourceModel

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"reviewDate": "2020-02-01T00:00:00Z", "source": "authority update"}]}
    )

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(
            review_date=authority_review.review_date, source=DataSourceModel.from_domain(authority_review.data_source)
        )

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=self.review_date, data_source=self.source.to_domain())


class CreateCapitalSchemeAuthorityReviewModel(BaseModel):
    source: DataSourceModel

    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "authority update"}]})

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
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    reference: Annotated[str, Path(examples=["ATE00001"])],
    authority_review_model: CreateCapitalSchemeAuthorityReviewModel,
) -> CapitalSchemeAuthorityReviewModel:
    """
    Creates an authority review for a capital scheme.
    """
    async with unit_of_work:
        capital_scheme = await capital_schemes.get(CapitalSchemeReference(reference))

        if not capital_scheme:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        authority_review = authority_review_model.to_domain(clock.now)
        capital_scheme.perform_authority_review(authority_review)
        await capital_schemes.update(capital_scheme)
        await unit_of_work.commit()

    return CapitalSchemeAuthorityReviewModel.from_domain(authority_review)
