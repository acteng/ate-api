from dataclasses import dataclass
from typing import Generator

import pytest
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi import FastAPI
from httpx import Client
from testcontainers.postgres import PostgresContainer

from ate_api.main import app
from ate_api.settings import Settings, get_settings
from tests.e2e import routes
from tests.e2e.app_client import AppClient
from tests.e2e.oauth.app import app as oauth_app
from tests.e2e.oauth.app import clients
from tests.e2e.oauth.clients import StubClient
from tests.e2e.oauth.settings import Settings as oauth_Settings
from tests.e2e.oauth.settings import get_settings as oauth_get_settings
from tests.e2e.server import Server


@dataclass(frozen=True)
class _Client:
    client_id: str
    client_secret: str


@dataclass(frozen=True)
class _ResourceServer:
    identifier: str


@pytest.fixture(name="database_url", scope="package")
def database_url_fixture() -> Generator[str]:
    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url(driver="pg8000")


@pytest.fixture(name="resource_server", scope="package")
def resource_server_fixture() -> _ResourceServer:
    return _ResourceServer(identifier="https://api.example")


@pytest.fixture(name="test_oauth_client", scope="package")
def test_oauth_client_fixture() -> _Client:
    return _Client(client_id="test", client_secret="secret")


@pytest.fixture(name="authorization_server_settings", scope="package")
def authorization_server_settings_fixture(resource_server: _ResourceServer) -> oauth_Settings:
    return oauth_Settings(resource_server_identifier=resource_server.identifier)


@pytest.fixture(name="authorization_server_app", scope="package")
def authorization_server_app_fixture(
    authorization_server_settings: oauth_Settings, test_oauth_client: _Client
) -> Generator[FastAPI]:
    oauth_app.dependency_overrides[oauth_get_settings] = lambda: authorization_server_settings
    clients.add(StubClient(client_id=test_oauth_client.client_id, client_secret=test_oauth_client.client_secret))
    yield oauth_app
    clients.clear()
    oauth_app.dependency_overrides = {}


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(authorization_server_app: FastAPI) -> Generator[Server]:
    server = Server(authorization_server_app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="authorization_client")
def authorization_client_fixture(test_oauth_client: _Client) -> OAuth2Client:
    return OAuth2Client(
        client_id=test_oauth_client.client_id,
        client_secret=test_oauth_client.client_secret,
        token_endpoint_auth_method="client_secret_post",
    )


@pytest.fixture(name="access_token")
def access_token_fixture(
    authorization_server: Server, resource_server: _ResourceServer, authorization_client: OAuth2Client
) -> str:
    token_endpoint = authorization_server.url + authorization_server.app.url_path_for("token")
    token: OAuth2Token = authorization_client.fetch_token(
        token_endpoint, grant_type="client_credentials", audience=resource_server.identifier
    )
    return str(token["access_token"])


@pytest.fixture(name="settings", scope="package")
def settings_fixture(database_url: str, authorization_server: Server, resource_server: _ResourceServer) -> Settings:
    oidc_server_metadata_url = authorization_server.url + authorization_server.app.url_path_for("openid_configuration")
    return Settings(
        database_url=database_url,
        create_database_schema=True,
        oidc_server_metadata_url=oidc_server_metadata_url,
        resource_server_identifier=resource_server.identifier,
    )


@pytest.fixture(name="app", scope="package")
def app_fixture(settings: Settings) -> Generator[FastAPI]:
    app.dependency_overrides[get_settings] = lambda: settings
    app.include_router(routes.router)
    yield app
    app.dependency_overrides = {}


@pytest.fixture(name="server", scope="package")
def server_fixture(app: FastAPI) -> Generator[Server]:
    server = Server(app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="client")
def client_fixture(server: Server) -> Client:
    return Client(base_url=server.url)


@pytest.fixture(name="app_client")
def app_client_fixture(server: Server, access_token: str) -> Generator[AppClient]:
    app_client = AppClient(server.url, access_token)
    yield app_client
    app_client.delete_capital_schemes()
    app_client.delete_authorities()
    app_client.delete_funding_programmes()
