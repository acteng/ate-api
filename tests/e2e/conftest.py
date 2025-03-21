from typing import Generator

import pytest
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi import FastAPI
from httpx import Client

import ate_api
from tests.e2e import oauth, routes
from tests.e2e.app_client import AppClient
from tests.e2e.oauth import StubClient, clients
from tests.e2e.server import Server


@pytest.fixture(name="resource_server_identifier", scope="package")
def resource_server_identifier_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="stub_client", scope="package")
def stub_client_fixture() -> StubClient:
    return StubClient(client_id="stub_client_id", client_secret="stub_client_secret")


@pytest.fixture(name="authorization_server_settings", scope="package")
def authorization_server_settings_fixture(resource_server_identifier: str) -> oauth.Settings:
    return oauth.Settings(resource_server_identifier=resource_server_identifier)


@pytest.fixture(name="authorization_server_app", scope="package")
def authorization_server_app_fixture(
    authorization_server_settings: oauth.Settings, stub_client: StubClient
) -> Generator[FastAPI, None, None]:
    oauth.app.dependency_overrides[oauth.get_settings] = lambda: authorization_server_settings
    clients.add(stub_client)
    yield oauth.app
    clients.clear()
    oauth.app.dependency_overrides = {}


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(authorization_server_app: FastAPI) -> Generator[Server, None, None]:
    server = Server(authorization_server_app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="oauth_client")
def oauth_client_fixture(stub_client: StubClient) -> OAuth2Client:
    return OAuth2Client(
        client_id=stub_client.client_id,
        client_secret=stub_client.client_secret,
        token_endpoint_auth_method="client_secret_post",
    )


@pytest.fixture(name="access_token")
def access_token_fixture(
    authorization_server: Server, resource_server_identifier: str, oauth_client: OAuth2Client
) -> str:
    token_endpoint = authorization_server.url + authorization_server.app.url_path_for("token")
    token: OAuth2Token = oauth_client.fetch_token(
        token_endpoint, grant_type="client_credentials", audience=resource_server_identifier
    )
    return str(token["access_token"])


@pytest.fixture(name="settings", scope="package")
def settings_fixture(authorization_server: Server, resource_server_identifier: str) -> ate_api.Settings:
    oidc_server_metadata_url = authorization_server.url + authorization_server.app.url_path_for("openid_configuration")
    return ate_api.Settings(
        oidc_server_metadata_url=oidc_server_metadata_url, resource_server_identifier=resource_server_identifier
    )


@pytest.fixture(name="app", scope="package")
def app_fixture(settings: ate_api.Settings) -> Generator[FastAPI, None, None]:
    ate_api.app.dependency_overrides[ate_api.get_settings] = lambda: settings
    ate_api.app.include_router(routes.router)
    yield ate_api.app
    ate_api.app.dependency_overrides = {}


@pytest.fixture(name="server", scope="package")
def server_fixture(app: FastAPI) -> Generator[Server, None, None]:
    server = Server(app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="client")
def client_fixture(server: Server) -> Client:
    return Client(base_url=server.url)


@pytest.fixture(name="app_client")
def app_client_fixture(server: Server, access_token: str) -> AppClient:
    return AppClient(server.url, access_token)
