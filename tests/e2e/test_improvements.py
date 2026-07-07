from httpx import AsyncClient

from tests.e2e.app_client import AppClient


async def test_get_improvement(client: AsyncClient, access_token: str, app_client: AppClient) -> None:
    await app_client.create_authority({"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"})
    await app_client.create_improvement(
        {
            "reference": "IMP00001",
            "overview": {
                "name": "Wirral Package",
                "description": 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                "fundingManagedBy": f"{client.base_url}/authorities/LIV",
                "source": "authority update",
            },
        }
    )

    response = await client.get("/improvements/IMP00001", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json() == {
        "@id": f"{client.base_url}/improvements/IMP00001",
        "reference": "IMP00001",
        "overview": {
            "name": "Wirral Package",
            "description": 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            "fundingManagedBy": f"{client.base_url}/authorities/LIV",
            "source": "authority update",
        },
    }
