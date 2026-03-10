from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ate_api.clock import get_clock
from ate_api.database import get_unit_of_work
from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancialsRepository
from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestonesRepository, MilestoneRepository
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeRepository
from ate_api.infrastructure.clock import Clock
from ate_api.main import app
from ate_api.repositories import (
    get_authority_repository,
    get_capital_scheme_financials_repository,
    get_capital_scheme_milestones_repository,
    get_capital_scheme_repository,
    get_funding_programme_repository,
    get_milestone_repository,
)
from ate_api.settings import Settings, get_settings
from ate_api.unit_of_work import UnitOfWork
from tests.integration.oauth import StubAuthorizationServer
from tests.unit.infrastructure.clock import FakeClock
from tests.unit.infrastructure.memory.authorities import MemoryAuthorityRepository
from tests.unit.infrastructure.memory.capital_scheme_financials import MemoryCapitalSchemeFinancialsRepository
from tests.unit.infrastructure.memory.capital_scheme_milestones import (
    MemoryCapitalSchemeMilestonesRepository,
    MemoryMilestoneRepository,
)
from tests.unit.infrastructure.memory.capital_schemes import MemoryCapitalSchemeRepository
from tests.unit.infrastructure.memory.funding_programmes import MemoryFundingProgrammeRepository
from tests.unit.infrastructure.memory.unit_of_work import FakeUnitOfWork


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


@pytest.fixture(name="clock")
def clock_fixture() -> Clock:
    return FakeClock()


@pytest.fixture(name="settings")
def settings_fixture(authorization_server: StubAuthorizationServer, resource_server_identifier: str) -> Settings:
    dummy_database_url = "sqlite:///:memory:"
    return Settings(
        database_url=dummy_database_url,
        oidc_server_metadata_url=authorization_server.configuration_endpoint,
        resource_server_identifier=resource_server_identifier,
    )


@pytest.fixture(name="unit_of_work")
def unit_of_work_fixture() -> UnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture(name="funding_programmes")
def funding_programmes_fixture() -> FundingProgrammeRepository:
    return MemoryFundingProgrammeRepository()


@pytest.fixture(name="authorities")
def authorities_fixture() -> AuthorityRepository:
    return MemoryAuthorityRepository()


@pytest.fixture(name="milestones")
def milestones_fixture() -> MilestoneRepository:
    return MemoryMilestoneRepository()


@pytest.fixture(name="capital_schemes")
def capital_schemes_fixture(capital_scheme_milestones: CapitalSchemeMilestonesRepository) -> CapitalSchemeRepository:
    return MemoryCapitalSchemeRepository(capital_scheme_milestones)


@pytest.fixture(name="capital_scheme_financials")
def capital_scheme_financials_fixture() -> CapitalSchemeFinancialsRepository:
    return MemoryCapitalSchemeFinancialsRepository()


@pytest.fixture(name="capital_scheme_milestones")
def capital_scheme_milestones_fixture() -> CapitalSchemeMilestonesRepository:
    return MemoryCapitalSchemeMilestonesRepository()


@pytest.fixture(name="app")
def app_fixture(
    clock: Clock,
    settings: Settings,
    unit_of_work: UnitOfWork,
    funding_programmes: FundingProgrammeRepository,
    authorities: AuthorityRepository,
    milestones: MilestoneRepository,
    capital_schemes: CapitalSchemeRepository,
    capital_scheme_financials: CapitalSchemeFinancialsRepository,
    capital_scheme_milestones: CapitalSchemeMilestonesRepository,
) -> Generator[FastAPI]:
    app.dependency_overrides[get_clock] = lambda: clock
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_unit_of_work] = lambda: unit_of_work
    app.dependency_overrides[get_funding_programme_repository] = lambda: funding_programmes
    app.dependency_overrides[get_authority_repository] = lambda: authorities
    app.dependency_overrides[get_milestone_repository] = lambda: milestones
    app.dependency_overrides[get_capital_scheme_repository] = lambda: capital_schemes
    app.dependency_overrides[get_capital_scheme_financials_repository] = lambda: capital_scheme_financials
    app.dependency_overrides[get_capital_scheme_milestones_repository] = lambda: capital_scheme_milestones
    yield app
    app.dependency_overrides = {}


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)
