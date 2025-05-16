from functools import lru_cache
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import OAuthFlowClientCredentials, OAuthFlows
from fastapi.security import HTTPAuthorizationCredentials, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from ate_api.settings import Settings, get_settings


class OAuth2ClientCredentialsBearer(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str | None,
        scopes: dict[str, str] = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(clientCredentials=OAuthFlowClientCredentials(tokenUrl=token_url, scopes=scopes))
        super().__init__(flows=flows, scheme_name=scheme_name, description=description, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth_scheme = OAuth2ClientCredentialsBearer(
    token_url="https://ate-api-dev.uk.auth0.com/oauth/token", scheme_name="auth0"
)


@lru_cache
def get_oauth(settings: Annotated[Settings, Depends(get_settings)]) -> OAuth:
    oauth = OAuth()
    oauth.register(name="auth0", server_metadata_url=settings.oidc_server_metadata_url)
    return oauth


async def authorize(
    settings: Annotated[Settings, Depends(get_settings)],
    oauth: Annotated[OAuth, Depends(get_oauth)],
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(oauth_scheme)],
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
                "aud": {"value": settings.resource_server_identifier},
            },
        )
    except Exception as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))

    # validate claims
    try:
        claims.validate()
    except (InvalidClaimError, ExpiredTokenError, InvalidTokenError) as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error))
