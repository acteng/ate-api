from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.funding_programmes import (
    FundingProgramme,
    FundingProgrammeRepository,
)
from ate_api.infrastructure.database.funding_programmes import (
    DatabaseFundingProgrammeRepository,
)
from ate_api.routes.base import BaseModel


class FundingProgrammeModel(BaseModel):
    code: str

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(code=funding_programme.code)

    def to_domain(self) -> FundingProgramme:
        return FundingProgramme(code=self.code)


router = APIRouter(prefix="/funding-programmes", tags=["funding-programmes"])


def get_funding_programme_repository(session: Annotated[Session, Depends(get_session)]) -> FundingProgrammeRepository:
    return DatabaseFundingProgrammeRepository(session)


@router.get("/{code}", summary="Get funding programme", responses={HTTP_404_NOT_FOUND: {}})
def get_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)], code: str
) -> FundingProgrammeModel:
    """
    Gets a funding programme.
    """
    funding_programme = funding_programmes.get(code)

    if not funding_programme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return FundingProgrammeModel.from_domain(funding_programme)
