from authlib.integrations.httpx_client import OAuth2Client
from httpx import Client

from tests.e2e.server import Server


def test_get_authority(
    authorization_server: Server, resource_server_identifier: str, oauth_client: OAuth2Client, client: Client
) -> None:
    token_endpoint = authorization_server.url + authorization_server.app.url_path_for("token")
    token = oauth_client.fetch_token(
        token_endpoint, grant_type="client_credentials", audience=resource_server_identifier
    )

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {token["access_token"]}"})

    assert response.status_code == 200
    assert response.json() == {"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"}
