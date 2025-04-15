from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.infrastructure.database.authorities import DatabaseAuthorityRepository
from ate_api.routes.links import get_path_parameter


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str
    bid_submitting_capital_schemes: str | None = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @staticmethod
    def link_to_identifier(link: str) -> str:
        abbreviation = get_path_parameter(link, "/authorities/{abbreviation}", "abbreviation")

        if abbreviation is None:
            raise ValueError(f"Invalid authority link: {link}")

        return abbreviation

    @classmethod
    def from_domain(cls, authority: Authority, app: Starlette) -> AuthorityModel:
        return AuthorityModel(
            abbreviation=authority.abbreviation,
            full_name=authority.full_name,
            bid_submitting_capital_schemes=app.url_path_for(
                "get_authority_bid_submitting_capital_schemes", abbreviation=authority.abbreviation
            ),
        )

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, full_name=self.full_name)


router = APIRouter()


def get_authority_repository(session: Annotated[Session, Depends(get_session)]) -> AuthorityRepository:
    return DatabaseAuthorityRepository(session)


@router.get("/authorities/{abbreviation}", summary="Get authority", responses={HTTP_404_NOT_FOUND: {}})
def get_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)], request: Request, abbreviation: str
) -> AuthorityModel:
    """
    Gets an authority.
    """
    authority = authorities.get(abbreviation)

    if not authority:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return AuthorityModel.from_domain(authority, request.app)
