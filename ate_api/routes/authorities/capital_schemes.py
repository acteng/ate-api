from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AnyUrl
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.routes.authorities.authorities import get_authority_repository
from ate_api.routes.capital_schemes.bid_statuses import CapitalSchemeBidStatusModel
from ate_api.routes.capital_schemes.capital_schemes import get_capital_scheme_repository
from ate_api.routes.collections import CollectionModel

router = APIRouter(prefix="/{abbreviation}/capital-schemes")


@router.get(
    "/bid-submitting", summary="Get authority bid submitting capital schemes", responses={HTTP_404_NOT_FOUND: {}}
)
def get_authority_bid_submitting_capital_schemes(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    abbreviation: str,
    bid_status: Annotated[CapitalSchemeBidStatusModel | None, Query(alias="bid-status")] = None,
) -> CollectionModel[AnyUrl]:
    """
    Gets the capital schemes submitted by an authority.
    """
    authority = authorities.get(abbreviation)

    if not authority:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    references = capital_schemes.get_references_by_bid_submitting_authority(
        abbreviation, bid_status=bid_status.to_domain() if bid_status else None
    )
    capital_scheme_links = [
        AnyUrl(str(request.url_for("get_capital_scheme", reference=reference))) for reference in references
    ]
    return CollectionModel[AnyUrl](items=capital_scheme_links)
