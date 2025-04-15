from fastapi import Depends, FastAPI
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN

from ate_api.auth import authorize
from ate_api.routes import authorities, capital_schemes


class HTTPError(BaseModel):
    detail: str


app = FastAPI(
    title="ATE API",
    description="The Active Travel England Web API.",
    dependencies=[Depends(authorize)],
    responses={HTTP_403_FORBIDDEN: {"model": HTTPError}},
)
app.include_router(authorities.router)
app.include_router(capital_schemes.router)
