from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AnyUrl
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from ate_api.domain.authorities import AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeCode, FundingProgrammeRepository
from ate_api.routes.authorities.authorities import get_authority_repository
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel
from ate_api.routes.capital_schemes.capital_schemes import get_capital_scheme_repository
from ate_api.routes.capital_schemes.milestones import MilestoneModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.funding_programmes import get_funding_programme_repository

router = APIRouter(prefix="/{abbreviation}/capital-schemes")


@router.get(
    "/bid-submitting", summary="Get authority bid submitting capital schemes", responses={HTTP_404_NOT_FOUND: {}}
)
async def get_authority_bid_submitting_capital_schemes(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    abbreviation: str,
    funding_programme_code: Annotated[str | None, Query(alias="funding-programme-code")] = None,
    bid_status: Annotated[BidStatusModel | None, Query(alias="bid-status")] = None,
    current_milestones: Annotated[list[MilestoneModel] | None, Query(alias="current-milestone")] = None,
) -> CollectionModel[AnyUrl]:
    """
    Gets the capital schemes submitted by an authority.
    """
    if not await authorities.exists(AuthorityAbbreviation(abbreviation)):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    if funding_programme_code:
        funding_programme = await funding_programmes.get(FundingProgrammeCode(funding_programme_code))

        if not funding_programme:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY)

    references = await capital_schemes.get_references_by_bid_submitting_authority(
        AuthorityAbbreviation(abbreviation),
        funding_programme_code=FundingProgrammeCode(funding_programme_code) if funding_programme_code else None,
        bid_status=bid_status.to_domain() if bid_status else None,
        current_milestones=[milestone.to_domain() for milestone in current_milestones] if current_milestones else None,
    )
    capital_scheme_links = [
        AnyUrl(str(request.url_for("get_capital_scheme", reference=str(reference)))) for reference in references
    ]
    return CollectionModel[AnyUrl](items=capital_scheme_links)
