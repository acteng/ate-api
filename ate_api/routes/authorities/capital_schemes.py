from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AnyUrl
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.authorities import AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.routes.authorities.authorities import get_authority_repository
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel
from ate_api.routes.capital_schemes.capital_schemes import get_capital_scheme_repository
from ate_api.routes.capital_schemes.milestones import MilestoneModel
from ate_api.routes.collections import CollectionModel

router = APIRouter(prefix="/{abbreviation}/capital-schemes")


@router.get(
    "/bid-submitting", summary="Get authority bid submitting capital schemes", responses={HTTP_404_NOT_FOUND: {}}
)
async def get_authority_bid_submitting_capital_schemes(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    abbreviation: str,
    bid_status: Annotated[BidStatusModel | None, Query(alias="bid-status")] = None,
    current_milestones: Annotated[list[MilestoneModel] | None, Query(alias="current-milestone")] = None,
) -> CollectionModel[AnyUrl]:
    """
    Gets the capital schemes submitted by an authority.
    """
    authority = await authorities.get(AuthorityAbbreviation(abbreviation))

    if not authority:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    references = await capital_schemes.get_references_by_bid_submitting_authority(
        AuthorityAbbreviation(abbreviation),
        bid_status=bid_status.to_domain() if bid_status else None,
        current_milestones=[milestone.to_domain() for milestone in current_milestones] if current_milestones else None,
    )
    capital_scheme_links = [
        AnyUrl(str(request.url_for("get_capital_scheme", reference=str(reference)))) for reference in references
    ]
    return CollectionModel[AnyUrl](items=capital_scheme_links)
