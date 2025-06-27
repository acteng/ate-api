from typing import Annotated, Self

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import AnyUrl
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.infrastructure.database.authorities import DatabaseAuthorityRepository
from ate_api.routes.base import BaseModel


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str
    bid_submitting_capital_schemes: AnyUrl | None = None

    @classmethod
    def from_domain(cls, authority: Authority, request: Request) -> Self:
        return cls(
            abbreviation=str(authority.abbreviation),
            full_name=authority.full_name,
            bid_submitting_capital_schemes=AnyUrl(
                str(
                    request.url_for(
                        "get_authority_bid_submitting_capital_schemes", abbreviation=str(authority.abbreviation)
                    )
                )
            ),
        )

    def to_domain(self) -> Authority:
        return Authority(abbreviation=AuthorityAbbreviation(self.abbreviation), full_name=self.full_name)


router = APIRouter()


def get_authority_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthorityRepository:
    return DatabaseAuthorityRepository(session)


@router.get("/{abbreviation}", summary="Get authority", responses={HTTP_404_NOT_FOUND: {}})
async def get_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)], request: Request, abbreviation: str
) -> AuthorityModel:
    """
    Gets an authority.
    """
    authority = await authorities.get(AuthorityAbbreviation(abbreviation))

    if not authority:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return AuthorityModel.from_domain(authority, request)
