from typing import Annotated, Literal, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import AnyUrl, ConfigDict, Field
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_CONTENT

from ate_api.domain.authorities import AuthorityAbbreviation, AuthorityRepository
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem, CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeCode, FundingProgrammeRepository
from ate_api.repositories import (
    get_authority_repository,
    get_capital_scheme_repository,
    get_funding_programme_repository,
)
from ate_api.routes.base import BaseModel
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel
from ate_api.routes.capital_schemes.milestones import MilestoneModel
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel
from ate_api.routes.collections import CollectionModel

router = APIRouter(prefix="/{abbreviation}/capital-schemes")


class CapitalSchemeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]
    reference: str
    overview: CapitalSchemeOverviewModel
    authority_review: CapitalSchemeAuthorityReviewModel | None

    @classmethod
    def from_domain(cls, capital_scheme_item: CapitalSchemeItem, request: Request) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_capital_scheme", reference=str(capital_scheme_item.reference)))),
            reference=str(capital_scheme_item.reference),
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme_item.overview, request),
            authority_review=(
                CapitalSchemeAuthorityReviewModel.from_domain(capital_scheme_item.authority_review)
                if capital_scheme_item.authority_review
                else None
            ),
        )


class CapitalSchemeItemsModel(CollectionModel[CapitalSchemeItemModel]):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE00001",
                            "reference": "ATE00001",
                            "overview": {
                                "name": "Wirral Package",
                                "bidSubmittingAuthority": "https://api.activetravelengland.gov.uk/authorities/LIV",
                                "fundingProgramme": "https://api.activetravelengland.gov.uk/funding-programmes/ATF3",
                                "type": "construction",
                            },
                            "authorityReview": {"reviewDate": "2020-02-01T00:00:00Z", "source": "authority update"},
                        },
                        {
                            "@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE00002",
                            "reference": "ATE00002",
                            "overview": {
                                "name": "School Streets",
                                "bidSubmittingAuthority": "https://api.activetravelengland.gov.uk/authorities/LIV",
                                "fundingProgramme": "https://api.activetravelengland.gov.uk/funding-programmes/ATF4",
                                "type": "construction",
                            },
                            "authorityReview": {"reviewDate": "2020-02-02T00:00:00Z", "source": "authority update"},
                        },
                        {
                            "@id": "https://api.activetravelengland.gov.uk/capital-schemes/ATE00003",
                            "reference": "ATE00003",
                            "overview": {
                                "name": "Hospital Fields Road",
                                "bidSubmittingAuthority": "https://api.activetravelengland.gov.uk/authorities/LIV",
                                "fundingProgramme": "https://api.activetravelengland.gov.uk/funding-programmes/ATF5",
                                "type": "construction",
                            },
                            "authorityReview": {"reviewDate": "2020-02-03T00:00:00Z", "source": "authority update"},
                        },
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

    capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
        AuthorityAbbreviation(abbreviation),
        funding_programme_codes=(
            [FundingProgrammeCode(code) for code in funding_programme_codes] if funding_programme_codes else None
        ),
        bid_status=bid_status.to_domain() if bid_status else None,
        current_milestones=[_to_domain(milestone) for milestone in current_milestones] if current_milestones else None,
    )
    capital_scheme_models = [
        CapitalSchemeItemModel.from_domain(capital_scheme_item, request) for capital_scheme_item in capital_scheme_items
    ]
    return CapitalSchemeItemsModel(items=capital_scheme_models)


def _to_domain(milestone: MilestoneModel | Literal[""]) -> Milestone | None:
    match milestone:
        case MilestoneModel():
            return milestone.to_domain()
        case "":
            return None
