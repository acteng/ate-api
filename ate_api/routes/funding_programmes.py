from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import AnyUrl
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.infrastructure.database.funding_programmes import DatabaseFundingProgrammeRepository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel


class FundingProgrammeModel(BaseModel):
    code: str

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(code=str(funding_programme.code))

    def to_domain(self) -> FundingProgramme:
        return FundingProgramme(code=FundingProgrammeCode(self.code))


router = APIRouter(prefix="/funding-programmes", tags=["funding-programmes"])


def get_funding_programme_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FundingProgrammeRepository:
    return DatabaseFundingProgrammeRepository(session)


@router.get("", summary="Get funding programmes")
async def get_funding_programmes(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    request: Request,
) -> CollectionModel[AnyUrl]:
    """
    Gets the funding programmes.
    """
    all_funding_programmes = await funding_programmes.get_all()
    funding_programme_links = [
        AnyUrl(str(request.url_for("get_funding_programme", code=str(funding_programme.code))))
        for funding_programme in all_funding_programmes
    ]
    return CollectionModel[AnyUrl](items=funding_programme_links)


@router.get("/{code}", summary="Get funding programme", responses={HTTP_404_NOT_FOUND: {}})
async def get_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)], code: str
) -> FundingProgrammeModel:
    """
    Gets a funding programme.
    """
    funding_programme = await funding_programmes.get(FundingProgrammeCode(code))

    if not funding_programme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return FundingProgrammeModel.from_domain(funding_programme)
