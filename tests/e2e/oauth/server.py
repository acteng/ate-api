import asyncio
from typing import Any, Callable

from authlib.oauth2 import AuthorizationServer, OAuth2Request
from authlib.oauth2.rfc6749 import ClientMixin
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class StarletteAuthorizationServer(AuthorizationServer):  # type: ignore
    def __init__(self, query_client: Callable[[str], ClientMixin]):
        super().__init__()
        self._query_client = query_client

    def query_client(self, client_id: str) -> ClientMixin:
        return self._query_client(client_id)

    def save_token(self, token: dict[str, str], request: OAuth2Request) -> None:
        # JWT Bearer tokens do not require saving
        pass

    def send_signal(self, name: str, *args: Any, **kwargs: Any) -> None:
        # Starlette does not support signal, so ignore
        pass

    def create_oauth2_request(self, request: Request) -> OAuth2Request:
        form = asyncio.run(self._get_form(request))
        return OAuth2Request(request.method, str(request.url), dict(form), request.headers)

    def handle_response(self, status: int, body: Any, headers: list[tuple[str, str]]) -> Response:
        return JSONResponse(body, status, dict(headers))

    @staticmethod
    async def _get_form(request: Request) -> FormData:
        async with request.form() as form:
            return form
