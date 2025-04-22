import respx
from fastapi.testclient import TestClient

from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeRepository


@respx.mock
def test_get_capital_scheme(capital_schemes: CapitalSchemeRepository, client: TestClient, access_token: str) -> None:
    capital_schemes.add(CapitalScheme(reference="ATE00001"))

    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {"reference": "ATE00001"}


@respx.mock
def test_get_capital_scheme_when_not_found(client: TestClient, access_token: str) -> None:
    response = client.get("/capital-schemes/ATE00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 404
