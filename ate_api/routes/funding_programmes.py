from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import AnyUrl, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.infrastructure.database.funding_programmes import DatabaseFundingProgrammeRepository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel


class FundingProgrammeModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    code: str
    eligible_for_authority_update: bool

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


router = APIRouter(prefix="/funding-programmes", tags=["funding-programmes"])


def get_funding_programme_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FundingProgrammeRepository:
    return DatabaseFundingProgrammeRepository(session)


@router.get("", summary="Get funding programmes")
async def get_funding_programmes(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    request: Request,
    is_eligible_for_authority_update: Annotated[bool | None, Query(alias="eligible-for-authority-update")] = None,
) -> CollectionModel[FundingProgrammeItemModel]:
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
    return CollectionModel[FundingProgrammeItemModel](items=funding_programme_models)


@router.get("/{code}", summary="Get funding programme", responses={HTTP_404_NOT_FOUND: {}})
async def get_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    request: Request,
    code: str,
) -> FundingProgrammeModel:
    """
    Gets a funding programme.
    """
    funding_programme = await funding_programmes.get(FundingProgrammeCode(code))

    if not funding_programme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return FundingProgrammeModel.from_domain(funding_programme, request)
