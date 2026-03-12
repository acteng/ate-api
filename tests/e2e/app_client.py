from typing import Any

from httpx import AsyncClient


class AppClient:
    def __init__(self, url: str, access_token: str):
        self._client = AsyncClient(http2=True, base_url=url, headers={"Authorization": f"Bearer {access_token}"})

    async def set_clock(self, now: str) -> None:
        response = await self._client.put("/test/clock", json=now)
        response.raise_for_status()

    async def create_funding_programme(self, funding_programme: Any) -> None:
        response = await self._client.post("/test/funding-programmes", json=funding_programme)
        response.raise_for_status()

    async def delete_funding_programmes(self) -> None:
        response = await self._client.delete("/test/funding-programmes")
        response.raise_for_status()

    async def create_authority(self, authority: Any) -> None:
        response = await self._client.post("/test/authorities", json=authority)
        response.raise_for_status()

    async def delete_authorities(self) -> None:
        response = await self._client.delete("/test/authorities")
        response.raise_for_status()

    async def create_capital_scheme(self, capital_scheme: Any) -> None:
        response = await self._client.post("/test/capital-schemes", json=capital_scheme)
        response.raise_for_status()

    async def create_capital_scheme_financial(self, capital_scheme: str, financial: Any) -> None:
        response = await self._client.post(f"/capital-schemes/{capital_scheme}/financials", json=financial)
        response.raise_for_status()

    async def create_capital_scheme_milestones(self, capital_scheme: str, milestones: Any) -> None:
        response = await self._client.post(f"/capital-schemes/{capital_scheme}/milestones", json=milestones)
        response.raise_for_status()

    async def create_capital_scheme_authority_review(self, capital_scheme: str, authority_review: Any) -> None:
        response = await self._client.post(
            f"/capital-schemes/{capital_scheme}/authority-reviews", json=authority_review
        )
        response.raise_for_status()

    async def delete_capital_schemes(self) -> None:
        response = await self._client.delete("/test/capital-schemes")
        response.raise_for_status()
