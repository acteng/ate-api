from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import AnyUrl, Field
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.repositories import get_authority_repository
from ate_api.routes.base import BaseModel


class AuthorityModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    abbreviation: str
    full_name: str
    bid_submitting_capital_schemes: AnyUrl | None = None

    @classmethod
    def from_domain(cls, authority: Authority, request: Request) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_authority", abbreviation=str(authority.abbreviation)))),
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
