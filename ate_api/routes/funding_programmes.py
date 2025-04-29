from __future__ import annotations

from typing import Annotated

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
from ate_api.routes.links import get_path_parameter


class FundingProgrammeModel(BaseModel):
    code: str

    @staticmethod
    def link_to_identifier(link: str) -> str:
        code = get_path_parameter(link, "/funding-programmes/{code}", "code")

        if code is None:
            raise ValueError(f"Invalid funding programme link: {link}")

        return code

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> FundingProgrammeModel:
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
