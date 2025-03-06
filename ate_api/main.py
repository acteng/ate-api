from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer_scheme = HTTPBearer()


@app.get("/")
async def index(authorization: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> dict[str, str]:
    return {"message": "Hello World"}
