from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain import Authority, AuthorityRepository
from ate_api.infrastructure.database import DatabaseAuthorityRepository


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_domain(cls, authority: Authority) -> AuthorityModel:
        return AuthorityModel(abbreviation=authority.abbreviation, full_name=authority.full_name)

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, full_name=self.full_name)


router = APIRouter(tags=["authorities"])


def get_authority_repository(session: Annotated[Session, Depends(get_session)]) -> AuthorityRepository:
    return DatabaseAuthorityRepository(session)


@router.get("/authorities/{abbreviation}", summary="Get authority", responses={HTTP_404_NOT_FOUND: {}})
def get_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)], abbreviation: str
) -> AuthorityModel:
    """
    Gets an authority.
    """
    authority = authorities.get(abbreviation)

    if not authority:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return AuthorityModel.from_domain(authority)
