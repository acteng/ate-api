from typing import Generator

import pytest
from authlib.integrations.httpx_client import OAuth2Client
from fastapi import FastAPI
from httpx import Client

from ate_api import main
from ate_api.settings import Settings, get_settings
from tests.e2e import oauth
from tests.e2e.oauth import StubClient, clients
from tests.e2e.server import Server


@pytest.fixture(name="stub_client")
def stub_client_fixture() -> StubClient:
    return StubClient(client_id="stub_client_id", client_secret="stub_client_secret")


@pytest.fixture(name="authorization_server_app")
def authorization_server_app_fixture(stub_client: StubClient) -> Generator[FastAPI, None, None]:
    clients.add(stub_client)
    yield oauth.app
    clients.clear()


@pytest.fixture(name="authorization_server")
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


@pytest.fixture(name="settings")
def settings_fixture(authorization_server: Server) -> Settings:
    oidc_server_metadata_url = authorization_server.url + authorization_server.app.url_path_for("openid_configuration")
    return Settings(oidc_server_metadata_url=oidc_server_metadata_url)


@pytest.fixture(name="app")
def app_fixture(settings: Settings) -> Generator[FastAPI, None, None]:
    main.app.dependency_overrides[get_settings] = lambda: settings
    yield main.app
    main.app.dependency_overrides = {}


@pytest.fixture(name="server")
def server_fixture(app: FastAPI) -> Generator[Server, None, None]:
    server = Server(app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="client")
def client_fixture(server: Server) -> Client:
    return Client(base_url=server.url)
