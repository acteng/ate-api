from typing import Generator

import pytest
import respx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ate_api.settings import Settings, get_settings
from tests.integration.oauth import StubAuthorizationServer


@pytest.fixture(name="resource_server_identifier", scope="module")
def resource_server_identifier_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="authorization_server", scope="module")
def authorization_server_fixture(resource_server_identifier: str) -> StubAuthorizationServer:
    authorization_server = StubAuthorizationServer(resource_server_identifier)
    authorization_server.given_configuration_endpoint_returns_configuration()
    return authorization_server


@pytest.fixture(name="settings")
def settings_fixture(authorization_server: StubAuthorizationServer, resource_server_identifier: str) -> Settings:
    return Settings(
        oidc_server_metadata_url=authorization_server.configuration_endpoint,
        resource_server_identifier=resource_server_identifier,
    )


@pytest.fixture(name="app")
def app_fixture(app: FastAPI, settings: Settings) -> Generator[FastAPI, None, None]:
    app.dependency_overrides[get_settings] = lambda: settings
    yield app
    app.dependency_overrides = {}


@respx.mock
def test_get_index(authorization_server: StubAuthorizationServer, client: TestClient) -> None:
    access_token = authorization_server.create_access_token()

    response = client.get("/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@respx.mock
def test_cannot_get_index_with_invalid_signature(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(signature="invalid_signature".encode())

    response = client.get("/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "bad_signature: "}


@respx.mock
def test_cannot_get_index_with_invalid_issuer(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(issuer="https://malicious.example/")

    response = client.get("/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": 'invalid_claim: Invalid claim "iss"'}


@respx.mock
def test_cannot_get_index_with_invalid_audience(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(audience="https://malicious.example/")

    response = client.get("/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": 'invalid_claim: Invalid claim "aud"'}


@respx.mock
def test_cannot_get_index_with_expired_access_token(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(expiration_time=1)

    response = client.get("/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "expired_token: The token is expired"}


def test_cannot_get_index_without_bearer(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 403
