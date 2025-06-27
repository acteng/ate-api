from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.infrastructure.database.capital_schemes.capital_schemes import DatabaseCapitalSchemeRepository
from ate_api.routes.base import BaseModel
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetailsModel
from ate_api.routes.capital_schemes.milestones import (
    CapitalSchemeMilestoneModel,
    CapitalSchemeMilestonesModel,
    MilestoneModel,
)
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    milestones: CapitalSchemeMilestonesModel
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, request: Request) -> Self:
        return cls(
            reference=str(capital_scheme.reference),
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme.overview, request),
            bid_status_details=CapitalSchemeBidStatusDetailsModel.from_domain(capital_scheme.bid_status_details),
            milestones=CapitalSchemeMilestonesModel(
                current_milestone=(
                    MilestoneModel.from_domain(capital_scheme.current_milestone)
                    if capital_scheme.current_milestone
                    else None
                ),
                items=[CapitalSchemeMilestoneModel.from_domain(milestone) for milestone in capital_scheme.milestones],
            ),
            authority_review=(
                CapitalSchemeAuthorityReviewModel.from_domain(capital_scheme.authority_review)
                if capital_scheme.authority_review
                else None
            ),
        )

    def to_domain(self, now: datetime, request: Request) -> CapitalScheme:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference(self.reference),
            overview=self.overview.to_domain(now, request),
            bid_status_details=self.bid_status_details.to_domain(now),
        )

        for milestone in self.milestones.items:
            capital_scheme.change_milestone(milestone.to_domain(now))

        if self.authority_review:
            capital_scheme.perform_authority_review(self.authority_review.to_domain())

        return capital_scheme


router = APIRouter()


def get_capital_scheme_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> CapitalSchemeRepository:
    return DatabaseCapitalSchemeRepository(session)


@router.get("/{reference}", summary="Get capital scheme", responses={HTTP_404_NOT_FOUND: {}})
async def get_capital_scheme(
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    reference: str,
) -> CapitalSchemeModel:
    """
    Gets a capital scheme.
    """
    capital_scheme = await capital_schemes.get(CapitalSchemeReference(reference))

    if not capital_scheme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return CapitalSchemeModel.from_domain(capital_scheme, request)
