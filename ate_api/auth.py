from functools import lru_cache
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.jose.errors import InvalidClaimError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ate_api.settings import Settings, get_settings

bearer_scheme = HTTPBearer()


@lru_cache
def get_oauth(settings: Annotated[Settings, Depends(get_settings)]) -> OAuth:
    oauth = OAuth()
    oauth.register(name="auth0", server_metadata_url=settings.oidc_server_metadata_url)
    return oauth


async def authorize(
    oauth: Annotated[OAuth, Depends(get_oauth)],
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> None:
    token = authorization.credentials
    server_metadata = await oauth.auth0.load_server_metadata()
    jwks = await oauth.auth0.fetch_jwk_set()

    # validate signature
    try:
        claims = jwt.decode(token, key=jwks, claims_options={"iss": {"value": server_metadata.get("issuer")}})
    except Exception as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))

    # validate claims
    try:
        claims.validate()
    except InvalidClaimError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))
