from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.status import HTTP_201_CREATED

from ate_api.authorities import (
    AuthorityModel,
    AuthorityRepository,
    get_authority_repository,
)

router = APIRouter()


@router.post("/test/authorities", status_code=HTTP_201_CREATED)
async def create_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)], authority: AuthorityModel
) -> None:
    authorities.add(authority.to_domain())
