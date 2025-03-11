from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from ate_api.auth import bearer_scheme

router = APIRouter()


@router.get("/")
async def index(authorization: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> dict[str, str]:
    return {"message": "Hello World"}
