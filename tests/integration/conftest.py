from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ate_api.domain import AuthorityRepository
from ate_api.infrastructure.memory import MemoryAuthorityRepository
from ate_api.main import app
from ate_api.routes import get_authority_repository
from ate_api.settings import Settings, get_settings
from tests.integration.oauth import StubAuthorizationServer


@pytest.fixture(name="resource_server_identifier", scope="package")
def resource_server_identifier_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(resource_server_identifier: str) -> StubAuthorizationServer:
    authorization_server = StubAuthorizationServer(resource_server_identifier)
    authorization_server.given_configuration_endpoint_returns_configuration()
    return authorization_server


@pytest.fixture(name="access_token")
def access_token_fixture(authorization_server: StubAuthorizationServer) -> str:
    return authorization_server.create_access_token()


@pytest.fixture(name="settings")
def settings_fixture(authorization_server: StubAuthorizationServer, resource_server_identifier: str) -> Settings:
    return Settings(
        oidc_server_metadata_url=authorization_server.configuration_endpoint,
        resource_server_identifier=resource_server_identifier,
    )


@pytest.fixture(name="authorities")
def authorities_fixture() -> AuthorityRepository:
    return MemoryAuthorityRepository()


@pytest.fixture(name="app")
def app_fixture(settings: Settings, authorities: AuthorityRepository) -> Generator[FastAPI]:
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_authority_repository] = lambda: authorities
    yield app
    app.dependency_overrides = {}


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)
