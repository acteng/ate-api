from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeRepository
from ate_api.main import app
from ate_api.routes.authorities.authorities import get_authority_repository
from ate_api.routes.capital_schemes.capital_schemes import get_capital_scheme_repository
from ate_api.routes.funding_programmes import get_funding_programme_repository
from ate_api.settings import Settings, get_settings
from tests.integration.memory import (
    MemoryAuthorityRepository,
    MemoryCapitalSchemeRepository,
    MemoryFundingProgrammeRepository,
)
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
    dummy_database_url = "sqlite:///:memory:"
    return Settings(
        database_url=dummy_database_url,
        oidc_server_metadata_url=authorization_server.configuration_endpoint,
        resource_server_identifier=resource_server_identifier,
    )


@pytest.fixture(name="funding_programmes")
def funding_programmes_fixture() -> FundingProgrammeRepository:
    return MemoryFundingProgrammeRepository()


@pytest.fixture(name="authorities")
def authorities_fixture() -> AuthorityRepository:
    return MemoryAuthorityRepository()


@pytest.fixture(name="capital_schemes")
def capital_schemes_fixture() -> CapitalSchemeRepository:
    return MemoryCapitalSchemeRepository()


@pytest.fixture(name="app")
def app_fixture(
    settings: Settings,
    funding_programmes: FundingProgrammeRepository,
    authorities: AuthorityRepository,
    capital_schemes: CapitalSchemeRepository,
) -> Generator[FastAPI]:
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_funding_programme_repository] = lambda: funding_programmes
    app.dependency_overrides[get_authority_repository] = lambda: authorities
    app.dependency_overrides[get_capital_scheme_repository] = lambda: capital_schemes
    yield app
    app.dependency_overrides = {}


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)
