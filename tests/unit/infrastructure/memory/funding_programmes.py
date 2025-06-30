from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository


class MemoryFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self) -> None:
        self._funding_programmes: dict[FundingProgrammeCode, FundingProgramme] = {}

    async def add(self, funding_programme: FundingProgramme) -> None:
        self._funding_programmes[funding_programme.code] = funding_programme

    async def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        return self._funding_programmes.get(code)

    async def exists(self, code: FundingProgrammeCode) -> bool:
        return code in self._funding_programmes
