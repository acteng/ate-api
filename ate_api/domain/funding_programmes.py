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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._code)})"


class FundingProgramme:
    def __init__(self, code: FundingProgrammeCode, is_eligible_for_authority_update: bool = False):
        self._code = code
        self._is_eligible_for_authority_update = is_eligible_for_authority_update

    @property
    def code(self) -> FundingProgrammeCode:
        return self._code

    @property
    def is_eligible_for_authority_update(self) -> bool:
        return self._is_eligible_for_authority_update


class FundingProgrammeRepository:
    async def add(self, funding_programme: FundingProgramme) -> None:
        raise NotImplementedError()

    async def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        raise NotImplementedError()

    async def get_all(self) -> list[FundingProgramme]:
        raise NotImplementedError()

    async def exists(self, code: FundingProgrammeCode) -> bool:
        raise NotImplementedError()

    async def exists_all(self, codes: list[FundingProgrammeCode]) -> bool:
        raise NotImplementedError()
