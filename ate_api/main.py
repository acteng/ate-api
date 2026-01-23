from contextlib import asynccontextmanager
from importlib.metadata import version
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.gzip import GZipMiddleware
from hypercorn.middleware import ProxyFixMiddleware
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from ate_api.auth import authorize
from ate_api.database import create_database_schema, get_engine
from ate_api.routes import authorities, capital_schemes, funding_programmes
from ate_api.settings import get_settings


class HTTPError(BaseModel):
    detail: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = app.dependency_overrides.get(get_settings, get_settings)()
    engine = app.dependency_overrides.get(get_engine, get_engine)(settings=settings)

    if settings.create_database_schema:
        await create_database_schema(engine)

    yield


app = FastAPI(
    title="ATE API",
    description="The Active Travel England Web API.",
    version=version("ate_api"),
    dependencies=[Depends(authorize)],
    middleware=[Middleware(GZipMiddleware)],
    lifespan=lifespan,
    responses={HTTP_401_UNAUTHORIZED: {"model": HTTPError}},
)
app.include_router(authorities.router)
app.include_router(capital_schemes.router)
app.include_router(funding_programmes.router)
# Workaround: https://github.com/pgjones/hypercorn/issues/179
# TODO: fix incompatible types
# TODO: fix middleware wrapping app from preventing e2e tests from accessing Starlette methods
proxy_app = ProxyFixMiddleware(app)  # type: ignore
