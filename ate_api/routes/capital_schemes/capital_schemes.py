from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import AnyUrl, Field
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFinancialsRepository
from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestones, CapitalSchemeMilestonesRepository
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.repositories import (
    get_capital_scheme_financials_repository,
    get_capital_scheme_milestones_repository,
    get_capital_scheme_repository,
)
from ate_api.routes.base import BaseModel
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetailsModel
from ate_api.routes.capital_schemes.financials import CapitalSchemeFinancialsModel
from ate_api.routes.capital_schemes.milestones import CapitalSchemeMilestonesModel
from ate_api.routes.capital_schemes.outputs import CapitalSchemeOutputModel
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel
from ate_api.routes.collections import CollectionModel


class CapitalSchemeModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    financials: CapitalSchemeFinancialsModel
    milestones: CapitalSchemeMilestonesModel
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    @classmethod
    def from_domain(
        cls,
        capital_scheme: CapitalScheme,
        financials: CapitalSchemeFinancials,
        milestones: CapitalSchemeMilestones,
        request: Request,
    ) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_capital_scheme", reference=str(capital_scheme.reference)))),
            reference=str(capital_scheme.reference),
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme.overview, request),
            bid_status_details=CapitalSchemeBidStatusDetailsModel.from_domain(capital_scheme.bid_status_details),
            financials=CapitalSchemeFinancialsModel.from_domain(financials),
            milestones=CapitalSchemeMilestonesModel.from_domain(milestones),
            outputs=CollectionModel[CapitalSchemeOutputModel](
                items=[CapitalSchemeOutputModel.from_domain(output) for output in capital_scheme.outputs]
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

        for output in self.outputs.items:
            capital_scheme.change_output(output.to_domain(now))

        return capital_scheme


router = APIRouter()


@router.get("/{reference}", summary="Get capital scheme", responses={HTTP_404_NOT_FOUND: {}})
async def get_capital_scheme(
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    capital_scheme_financials: Annotated[
        CapitalSchemeFinancialsRepository, Depends(get_capital_scheme_financials_repository)
    ],
    capital_scheme_milestones: Annotated[
        CapitalSchemeMilestonesRepository, Depends(get_capital_scheme_milestones_repository)
    ],
    request: Request,
    reference: str,
) -> CapitalSchemeModel:
    """
    Gets a capital scheme.
    """
    capital_scheme = await capital_schemes.get(CapitalSchemeReference(reference))

    if not capital_scheme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    financials = await capital_scheme_financials.get(CapitalSchemeReference(reference))
    assert financials

    milestones = await capital_scheme_milestones.get(CapitalSchemeReference(reference))
    assert milestones

    return CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, request)
