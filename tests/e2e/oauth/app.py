from functools import lru_cache
from typing import Annotated, Any

from authlib.jose import KeySet, RSAKey
from authlib.oauth2 import AuthorizationServer
from fastapi import Depends, FastAPI, Request, Response

from tests.e2e.oauth.clients import ClientRepository
from tests.e2e.oauth.grants import PrivateKeyJwtClientCredentialsGrant
from tests.e2e.oauth.jwts import PrivateKeyJwtClientAssertion
from tests.e2e.oauth.servers import StarletteAuthorizationServer, SyncStarletteHttpRequest
from tests.e2e.oauth.settings import Settings, get_settings
from tests.e2e.oauth.tokens import StubJWTBearerTokenGenerator

app = FastAPI()
clients = ClientRepository()
_issuer = "https://stub.example"
_token_key = RSAKey.generate_key(is_private=True)


@lru_cache
def _get_authorization_server(
    settings: Annotated[Settings, Depends(get_settings)], request: Request
) -> AuthorizationServer:
    authorization_server = StarletteAuthorizationServer(clients.get)
    authorization_server.register_token_generator(
        "default", StubJWTBearerTokenGenerator(_issuer, settings.resource_server_identifier, KeySet([_token_key]))
    )
    authorization_server.register_client_auth_method(
        PrivateKeyJwtClientAssertion.CLIENT_AUTH_METHOD,
        PrivateKeyJwtClientAssertion(str(request.url_for("token")), _issuer, settings.resource_server_identifier),
    )
    authorization_server.register_grant(PrivateKeyJwtClientCredentialsGrant)
    return authorization_server


@app.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> dict[str, str]:
    return {
        "issuer": _issuer,
        "token_endpoint": str(request.url_for("token")),
        "jwks_uri": str(request.url_for("key_set")),
    }


@app.get("/.well-known/jwks.json")
async def key_set() -> Any:
    return KeySet([_token_key]).as_dict()


@app.post("/token")
async def token(
    authorization_server: Annotated[AuthorizationServer, Depends(_get_authorization_server)], request: Request
) -> Response:
    # Adapt Starlette's async HTTP request for Authlib's sync AuthorizationServer API
    async with request.form() as form:
        sync_request = SyncStarletteHttpRequest(request.method, request.url, request.headers, form)

    response: Response = authorization_server.create_token_response(sync_request)
    return response
