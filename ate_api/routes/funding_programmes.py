from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import AnyUrl, ConfigDict, Field
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.repositories import get_funding_programme_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel


class FundingProgrammeModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    code: str
    eligible_for_authority_update: bool

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "@id": "https://api.activetravelengland.gov.uk/funding-programmes/ATF3",
                    "code": "ATF3",
                    "eligibleForAuthorityUpdate": True,
                }
            ]
        }
    )

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme, request: Request) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_funding_programme", code=str(funding_programme.code)))),
            code=str(funding_programme.code),
            eligible_for_authority_update=funding_programme.is_eligible_for_authority_update,
        )

    def to_domain(self) -> FundingProgramme:
        return FundingProgramme(
            code=FundingProgrammeCode(self.code), is_eligible_for_authority_update=self.eligible_for_authority_update
        )


class FundingProgrammeItemModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    code: str

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme, request: Request) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_funding_programme", code=str(funding_programme.code)))),
            code=str(funding_programme.code),
        )


class FundingProgrammeItemsModel(CollectionModel[FundingProgrammeItemModel]):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {"@id": "https://api.activetravelengland.gov.uk/funding-programmes/ATF3", "code": "ATF3"},
                        {"@id": "https://api.activetravelengland.gov.uk/funding-programmes/ATF4", "code": "ATF4"},
                        {"@id": "https://api.activetravelengland.gov.uk/funding-programmes/ATF5", "code": "ATF5"},
                    ]
                }
            ]
        }
    )


router = APIRouter(prefix="/funding-programmes", tags=["funding-programmes"])


@router.get("", summary="Get funding programmes")
async def get_funding_programmes(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    request: Request,
    is_eligible_for_authority_update: Annotated[
        bool | None, Query(alias="eligible-for-authority-update", examples=[True])
    ] = None,
) -> FundingProgrammeItemsModel:
    """
    Gets the funding programmes.
    """
    all_funding_programmes = await funding_programmes.get_all(
        is_eligible_for_authority_update=is_eligible_for_authority_update
    )
    funding_programme_models = [
        FundingProgrammeItemModel.from_domain(funding_programme, request)
        for funding_programme in all_funding_programmes
    ]
    return FundingProgrammeItemsModel(items=funding_programme_models)


@router.get("/{code}", summary="Get funding programme", responses={HTTP_404_NOT_FOUND: {}})
async def get_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    request: Request,
    code: Annotated[str, Path(examples=["ATF3"])],
) -> FundingProgrammeModel:
    """
    Gets a funding programme.
    """
    funding_programme = await funding_programmes.get(FundingProgrammeCode(code))

    if not funding_programme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return FundingProgrammeModel.from_domain(funding_programme, request)
