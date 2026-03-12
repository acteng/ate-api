from dataclasses import dataclass
from typing import Any, AsyncGenerator, Generator

import pytest
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from fastapi import FastAPI
from httpx import AsyncClient, Client
from testcontainers.postgres import PostgresContainer

from ate_api.clock import get_clock
from ate_api.infrastructure.clock import Clock
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
from tests.unit.infrastructure.clock import FakeClock


@dataclass(frozen=True)
class OAuthClient:
    client_id: str
    public_key: bytes


@dataclass(frozen=True)
class OAuthResourceServer:
    identifier: str


# region app fixtures


@pytest.fixture(name="clock", scope="package")
def clock_fixture() -> Clock:
    return FakeClock()


@pytest.fixture(name="database_url", scope="package")
def database_url_fixture() -> Generator[str]:
    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url(driver="asyncpg")


@pytest.fixture(name="resource_server", scope="package")
def resource_server_fixture() -> OAuthResourceServer:
    return OAuthResourceServer(identifier="https://api.example")


@pytest.fixture(name="settings", scope="package")
def settings_fixture(
    database_url: str, authorization_server_metadata_url: str, resource_server: OAuthResourceServer
) -> Settings:
    return Settings(
        database_url=database_url,
        create_database_schema=True,
        oidc_server_metadata_url=authorization_server_metadata_url,
        resource_server_identifier=resource_server.identifier,
    )


@pytest.fixture(name="app", scope="package")
def app_fixture(clock: Clock, settings: Settings) -> Generator[FastAPI]:
    app.dependency_overrides[get_clock] = lambda: clock
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
def client_fixture(server: Server) -> AsyncClient:
    return AsyncClient(base_url=server.url)


@pytest.fixture(name="access_token")
def access_token_fixture(
    authorization_server_metadata: Any, resource_server: OAuthResourceServer, authorization_client: OAuth2Client
) -> str:
    token_endpoint = authorization_server_metadata["token_endpoint"]
    token: OAuth2Token = authorization_client.fetch_token(
        token_endpoint, grant_type="client_credentials", audience=resource_server.identifier
    )
    return str(token["access_token"])


@pytest.fixture(name="app_client")
async def app_client_fixture(server: Server, access_token: str) -> AsyncGenerator[AppClient]:
    app_client = AppClient(server.url, access_token)
    yield app_client
    await app_client.delete_capital_schemes()
    await app_client.delete_authorities()
    await app_client.delete_funding_programmes()


# endregion


# region authorization server fixtures


@pytest.fixture(name="authorization_server_settings", scope="package")
def authorization_server_settings_fixture(resource_server: OAuthResourceServer) -> oauth_Settings:
    return oauth_Settings(resource_server_identifier=resource_server.identifier)


@pytest.fixture(name="authorization_server_app", scope="package")
def authorization_server_app_fixture(
    authorization_server_settings: oauth_Settings, tests_oauth_client: OAuthClient
) -> Generator[FastAPI]:
    oauth_app.dependency_overrides[oauth_get_settings] = lambda: authorization_server_settings
    clients.add(StubClient(client_id=tests_oauth_client.client_id, public_key=tests_oauth_client.public_key))
    yield oauth_app
    clients.clear()
    oauth_app.dependency_overrides = {}


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(authorization_server_app: FastAPI) -> Generator[Server]:
    server = Server(authorization_server_app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="authorization_server_metadata_url", scope="package")
def authorization_server_metadata_url_fixture(authorization_server: Server) -> str:
    return authorization_server.url + authorization_server.app.url_path_for("openid_configuration")


@pytest.fixture(name="authorization_server_metadata", scope="package")
def authorization_server_metadata_fixture(authorization_server_metadata_url: str) -> Any:
    with Client() as client:
        response = client.get(authorization_server_metadata_url)
        response.raise_for_status()
        return response.json()


@pytest.fixture(name="tests_key_pair", scope="package")
def tests_key_pair_fixture() -> RSAPrivateKey:
    return rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)


@pytest.fixture(name="tests_private_key", scope="package")
def tests_private_key_fixture(tests_key_pair: RSAPrivateKey) -> bytes:
    return tests_key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())


@pytest.fixture(name="tests_public_key", scope="package")
def tests_public_key_fixture(tests_key_pair: RSAPrivateKey) -> bytes:
    return tests_key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)


@pytest.fixture(name="tests_oauth_client", scope="package")
def tests_oauth_client_fixture(tests_public_key: bytes) -> OAuthClient:
    return OAuthClient(client_id="tests", public_key=tests_public_key)


@pytest.fixture(name="authorization_client")
def authorization_client_fixture(
    tests_oauth_client: OAuthClient, tests_private_key: bytes, authorization_server_metadata: Any
) -> OAuth2Client:
    issuer = authorization_server_metadata["issuer"]
    return OAuth2Client(
        client_id=tests_oauth_client.client_id,
        client_secret=tests_private_key,
        # Workaround: https://github.com/authlib/authlib/issues/730
        token_endpoint_auth_method=PrivateKeyJWT(token_endpoint=issuer),
    )


# endregion
