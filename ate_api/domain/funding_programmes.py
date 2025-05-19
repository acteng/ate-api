from typing import Any


class FundingProgrammeCode:
    def __init__(self, code: str):
        self._code = code

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, FundingProgrammeCode) and self._code == other._code

    def __hash__(self) -> int:
        return hash(self._code)

    def __str__(self) -> str:
        return self._code


class FundingProgramme:
    def __init__(self, code: FundingProgrammeCode):
        self._code = code

    @property
    def code(self) -> FundingProgrammeCode:
        return self._code


class FundingProgrammeRepository:
    def add(self, funding_programme: FundingProgramme) -> None:
        raise NotImplementedError()

    def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        raise NotImplementedError()
