from typing import Any

from httpx import Client


class AppClient:
    def __init__(self, url: str, access_token: str):
        self._client = Client(base_url=url, headers={"Authorization": f"Bearer {access_token}"})

    def create_authority(self, authority: Any) -> None:
        response = self._client.post("/test/authorities", json=authority)
        response.raise_for_status()

    def delete_authorities(self) -> None:
        response = self._client.delete("/test/authorities")
        response.raise_for_status()

    def create_capital_scheme(self, capital_scheme: Any) -> None:
        response = self._client.post("/test/capital-schemes", json=capital_scheme)
        response.raise_for_status()

    def delete_capital_schemes(self) -> None:
        response = self._client.delete("/test/capital-schemes")
        response.raise_for_status()
