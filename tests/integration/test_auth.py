from datetime import datetime

import respx
from fastapi.testclient import TestClient

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from tests.integration.oauth import StubAuthorizationServer


@respx.mock
async def test_can_access_with_valid_access_token(
    authorities: AuthorityRepository, client: TestClient, access_token: str
) -> None:
    await authorities.add(
        Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
    )

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200


@respx.mock
def test_cannot_access_with_invalid_signature(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(signature=b"invalid_signature")

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "bad_signature: "}


@respx.mock
def test_cannot_access_with_missing_issuer(authorization_server: StubAuthorizationServer, client: TestClient) -> None:
    access_token = authorization_server.create_access_token(issuer=None)

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "missing_claim: Missing 'iss' claim"}


@respx.mock
def test_cannot_access_with_invalid_issuer(authorization_server: StubAuthorizationServer, client: TestClient) -> None:
    access_token = authorization_server.create_access_token(issuer="https://malicious.example/")

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "invalid_claim: Invalid claim 'iss'"}


@respx.mock
def test_cannot_access_with_missing_audience(authorization_server: StubAuthorizationServer, client: TestClient) -> None:
    access_token = authorization_server.create_access_token(audience=None)

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "missing_claim: Missing 'aud' claim"}


@respx.mock
def test_cannot_access_with_invalid_audience(authorization_server: StubAuthorizationServer, client: TestClient) -> None:
    access_token = authorization_server.create_access_token(audience="https://malicious.example/")

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "invalid_claim: Invalid claim 'aud'"}


@respx.mock
def test_cannot_access_with_missing_expiration_time(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(expiration_time=None)

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "missing_claim: Missing 'exp' claim"}


@respx.mock
def test_cannot_access_with_expired_access_token(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(expiration_time=1)

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "expired_token: The token is expired"}


@respx.mock
def test_cannot_access_with_missing_issued_at(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(issued_at=None)

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "missing_claim: Missing 'iat' claim"}


@respx.mock
def test_cannot_access_with_access_token_issued_in_future(
    authorization_server: StubAuthorizationServer, client: TestClient
) -> None:
    access_token = authorization_server.create_access_token(issued_at=int(datetime(3000, 1, 1).timestamp()))

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "invalid_token: The token is not valid as it was issued in the future"}


def test_cannot_access_without_bearer(client: TestClient) -> None:
    response = client.get("/authorities/LIV")

    assert response.status_code == 403
