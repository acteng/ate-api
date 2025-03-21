import respx
from fastapi.testclient import TestClient

from ate_api.authorities import Authority, AuthorityRepository


@respx.mock
def test_get_authority(authorities: AuthorityRepository, client: TestClient, access_token: str) -> None:
    authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"}


@respx.mock
def test_get_authority_when_not_found(authorities: AuthorityRepository, client: TestClient, access_token: str) -> None:
    response = client.get("/authorities/LIV", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
