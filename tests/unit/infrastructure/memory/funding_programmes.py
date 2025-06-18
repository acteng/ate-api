from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository


class MemoryFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self) -> None:
        self._funding_programmes: dict[FundingProgrammeCode, FundingProgramme] = {}

    def add(self, funding_programme: FundingProgramme) -> None:
        self._funding_programmes[funding_programme.code] = funding_programme

    def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        return self._funding_programmes.get(code)
