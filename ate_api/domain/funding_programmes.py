class FundingProgramme:
    def __init__(self, code: str):
        self._code = code

    @property
    def code(self) -> str:
        return self._code


class FundingProgrammeRepository:
    def add(self, funding_programme: FundingProgramme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()
