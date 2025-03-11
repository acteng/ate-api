from typing import Any

from authlib.jose import KeySet, RSAKey
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from tests.e2e.oauth.clients import ClientRepository
from tests.e2e.oauth.grants import ClientSecretPostClientCredentialsGrant
from tests.e2e.oauth.server import StarletteAuthorizationServer
from tests.e2e.oauth.tokens import StubJWTBearerTokenGenerator

app = FastAPI()
clients = ClientRepository()
_issuer = "https://stub.example"
_key = RSAKey.generate_key(is_private=True)
_authorization_server = StarletteAuthorizationServer(clients.get)
_authorization_server.register_grant(ClientSecretPostClientCredentialsGrant)
_authorization_server.register_token_generator("default", StubJWTBearerTokenGenerator(_issuer, KeySet([_key])))


@app.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> dict[str, str]:
    return {"issuer": _issuer, "jwks_uri": str(request.url_for("key_set"))}


@app.get("/.well-known/jwks.json")
async def key_set() -> Any:
    return KeySet([_key]).as_dict()


@app.post("/token")
def token(request: Request) -> Response:
    response: Response = _authorization_server.create_token_response(request)
    return response
