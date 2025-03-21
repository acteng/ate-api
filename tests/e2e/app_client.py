from typing import Any

from httpx import Client


class AppClient:
    def __init__(self, url: str, access_token: str):
        self._client = Client(base_url=url, headers={"Authorization": f"Bearer {access_token}"})

    def create_authority(self, authority: Any) -> None:
        response = self._client.post("/test/authorities", json=authority)
        response.raise_for_status()
