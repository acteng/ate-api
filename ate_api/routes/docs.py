from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import HTMLResponse, JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from ate_api.settings import Settings, get_settings

basic_auth = HTTPBasic(auto_error=False)


async def authorize(
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
) -> None:
    if not (settings.docs_username and settings.docs_password):
        return

    if not credentials:
        raise basic_auth.make_not_authenticated_error()

    if not (
        compare_digest(credentials.username, settings.docs_username)
        and compare_digest(credentials.password, settings.docs_password)
    ):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers=basic_auth.make_authenticate_headers(),
        )


router = APIRouter(dependencies=[Depends(authorize)], include_in_schema=False)


@router.get("/openapi.json")
async def openapi(request: Request) -> JSONResponse:
    # Simplified copy of FastAPI.setup.openapi
    return JSONResponse(request.app.openapi())


@router.get("/docs")
async def swagger_ui_html(request: Request) -> HTMLResponse:
    # Simplified copy of FastAPI.setup.swagger_ui_html
    return get_swagger_ui_html(
        openapi_url=request.app.url_path_for("openapi"),
        title=f"{request.app.title} - Swagger UI",
        swagger_ui_parameters=request.app.swagger_ui_parameters,
    )
