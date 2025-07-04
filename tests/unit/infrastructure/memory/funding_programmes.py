from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository


class MemoryFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self) -> None:
        self._funding_programmes: dict[FundingProgrammeCode, FundingProgramme] = {}

    async def add(self, funding_programme: FundingProgramme) -> None:
        self._funding_programmes[funding_programme.code] = funding_programme

    async def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        return self._funding_programmes.get(code)

    async def get_all(self, is_eligible_for_authority_update: bool | None = None) -> list[FundingProgramme]:
        return sorted(
            [
                funding_programme
                for funding_programme in self._funding_programmes.values()
                if (
                    is_eligible_for_authority_update is None
                    or funding_programme.is_eligible_for_authority_update == is_eligible_for_authority_update
                )
            ],
            key=lambda funding_programme: str(funding_programme.code),
        )

    async def exists(self, code: FundingProgrammeCode) -> bool:
        return code in self._funding_programmes

    async def exists_all(self, codes: list[FundingProgrammeCode]) -> bool:
        return all(code in self._funding_programmes for code in codes)
