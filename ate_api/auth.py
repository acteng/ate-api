from functools import lru_cache
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError, InvalidTokenError, MissingClaimError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ate_api.settings import Settings, get_settings

bearer_scheme = HTTPBearer(bearerFormat="JWT")


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

    # validate signature
    try:
        claims = jwt.decode(
            token,
            key=jwks,
            claims_options={
                "iss": {"value": server_metadata.get("issuer")},
                "aud": {"essential": True, "value": settings.resource_server_identifier},
            },
        )
    except Exception as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))

    # validate claims
    try:
        claims.validate()
    except (MissingClaimError, InvalidClaimError, ExpiredTokenError, InvalidTokenError) as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))
