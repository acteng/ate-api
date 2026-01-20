from typing import Any, Callable

from authlib.oauth2 import AuthorizationServer, OAuth2Request
from authlib.oauth2.rfc6749 import ClientMixin
from authlib.oauth2.rfc6749.requests import BasicOAuth2Payload
from starlette.datastructures import URL, FormData, Headers, UploadFile
from starlette.responses import JSONResponse, Response


class SyncStarletteHttpRequest:
    """
    Sync HTTP request adapter for Starlette's async HTTP request.
    """

    def __init__(self, method: str, url: URL, headers: Headers, form: FormData):
        self._method = method
        self._url = url
        self._headers = headers
        self._form = form

    @property
    def method(self) -> str:
        return self._method

    @property
    def url(self) -> URL:
        return self._url

    @property
    def headers(self) -> Headers:
        return self._headers

    @property
    def form(self) -> FormData:
        return self._form


class StarletteOAuth2Request(OAuth2Request):  # type: ignore
    def __init__(self, request: SyncStarletteHttpRequest):
        super().__init__(request.method, str(request.url), request.headers)
        self._form = request.form
        self.payload = BasicOAuth2Payload(self._form)

    @property
    def form(self) -> dict[str, UploadFile | str]:
        return dict(self._form)


# Workaround: https://github.com/authlib/authlib/pull/278
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

    def create_oauth2_request(self, request: SyncStarletteHttpRequest) -> OAuth2Request:
        return StarletteOAuth2Request(request)

    def handle_response(self, status: int, body: Any, headers: list[tuple[str, str]]) -> Response:
        return JSONResponse(body, status, dict(headers))
