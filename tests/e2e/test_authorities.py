import pytest
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from httpx import Client

from tests.e2e.server import Server


@pytest.fixture(name="access_token")
def access_token_fixture(
    authorization_server: Server, resource_server_identifier: str, oauth_client: OAuth2Client
) -> str:
    token_endpoint = authorization_server.url + authorization_server.app.url_path_for("token")
    token: OAuth2Token = oauth_client.fetch_token(
        token_endpoint, grant_type="client_credentials", audience=resource_server_identifier
    )
    return str(token["access_token"])


def test_get_authority(access_token: str, client: Client) -> None:
    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"}
