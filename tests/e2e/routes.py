from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ate_api.database import get_session
from ate_api.domain.authorities import AuthorityRepository
from ate_api.routes.authorities.authorities import (
    AuthorityModel,
    get_authority_repository,
)

router = APIRouter()


@router.post("/test/authorities", status_code=HTTP_201_CREATED, response_class=Response)
def create_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    session: Annotated[Session, Depends(get_session)],
    authority: AuthorityModel,
) -> None:
    authorities.add(authority.to_domain())
    session.commit()


@router.delete("/test/authorities", status_code=HTTP_204_NO_CONTENT)
def delete_authorities(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    authorities.clear()
    session.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)
