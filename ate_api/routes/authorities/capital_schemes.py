from typing import Annotated, Literal, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import AnyUrl, ConfigDict, Field
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_CONTENT

from ate_api.domain.authorities import AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.funding_programmes import FundingProgrammeCode, FundingProgrammeRepository
from ate_api.repositories import (
    get_authority_repository,
    get_capital_scheme_repository,
    get_funding_programme_repository,
)
from ate_api.routes.base import BaseModel
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel
from ate_api.routes.capital_schemes.milestones import MilestoneModel
from ate_api.routes.collections import CollectionModel

router = APIRouter(prefix="/{abbreviation}/capital-schemes")


class CapitalSchemeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]

    @classmethod
    def from_domain(cls, reference: CapitalSchemeReference, request: Request) -> Self:
        return cls(id=AnyUrl(str(request.url_for("get_capital_scheme", reference=str(reference)))))


class CapitalSchemeItemsModel(CollectionModel[CapitalSchemeItemModel]):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {"@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE000001"},
                        {"@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE000002"},
                        {"@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE000003"},
                    ]
                }
            ]
        }
    )


@router.get(
    "/bid-submitting", summary="Get authority bid submitting capital schemes", responses={HTTP_404_NOT_FOUND: {}}
)
async def get_authority_bid_submitting_capital_schemes(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    abbreviation: Annotated[str, Path(examples=["LIV"])],
    funding_programme_codes: Annotated[
        list[str] | None, Query(alias="funding-programme-code", examples=["ATF3"])
    ] = None,
    bid_status: Annotated[BidStatusModel | None, Query(alias="bid-status", examples=["funded"])] = None,
    current_milestones: Annotated[
        list[MilestoneModel | Literal[""]] | None,
        Query(alias="current-milestone", examples=["detailed design completed"]),
    ] = None,
) -> CapitalSchemeItemsModel:
    """
    Gets the capital schemes submitted by an authority.
    """
    if not await authorities.exists(AuthorityAbbreviation(abbreviation)):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    if funding_programme_codes and not await funding_programmes.exists_all(
        [FundingProgrammeCode(code) for code in funding_programme_codes]
    ):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_CONTENT)

    references = await capital_schemes.get_references_by_bid_submitting_authority(
        AuthorityAbbreviation(abbreviation),
        funding_programme_codes=(
            [FundingProgrammeCode(code) for code in funding_programme_codes] if funding_programme_codes else None
        ),
        bid_status=bid_status.to_domain() if bid_status else None,
        current_milestones=[_to_domain(milestone) for milestone in current_milestones] if current_milestones else None,
    )
    capital_scheme_models = [CapitalSchemeItemModel.from_domain(reference, request) for reference in references]
    return CapitalSchemeItemsModel(items=capital_scheme_models)


def _to_domain(milestone: MilestoneModel | Literal[""]) -> Milestone | None:
    match milestone:
        case MilestoneModel():
            return milestone.to_domain()
        case "":
            return None
