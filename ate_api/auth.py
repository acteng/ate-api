from functools import lru_cache
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from authlib.jose import KeySet
from authlib.jose.errors import BadSignatureError
from authlib.oauth2.rfc6750 import InvalidTokenError
from authlib.oauth2.rfc9068 import JWTBearerTokenValidator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ate_api.settings import Settings, get_settings

bearer_scheme = HTTPBearer(bearerFormat="JWT")


class MyJWTBearerTokenValidator(JWTBearerTokenValidator):  # type: ignore
    def __init__(self, issuer: str, resource_server: str, jwks: KeySet):
        super().__init__(issuer, resource_server)
        self._jwks = jwks

    def get_jwks(self) -> KeySet:
        return self._jwks


@lru_cache
def get_oauth(settings: Annotated[Settings, Depends(get_settings)]) -> OAuth:
    oauth = OAuth()
    oauth.register(name="auth0", server_metadata_url=settings.oidc_server_metadata_url)
    return oauth


async def authorize(
    settings: Annotated[Settings, Depends(get_settings)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> None:
    token = authorization.credentials
    server_metadata = await oauth.auth0.load_server_metadata()
    jwks = await oauth.auth0.fetch_jwk_set()

    token_validator = MyJWTBearerTokenValidator(
        issuer=server_metadata.get("issuer"), resource_server=settings.resource_server_identifier, jwks=jwks
    )

    # validate signature
    try:
        claims = token_validator.authenticate_token(token)
    except BadSignatureError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))

    # validate claims
    try:
        token_validator.validate_token(claims, scopes=None, request=None)
    except InvalidTokenError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))
