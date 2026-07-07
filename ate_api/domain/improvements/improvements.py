from typing import Any

from ate_api.domain.improvements.overviews import ImprovementOverview


class ImprovementReference:
    def __init__(self, reference: str):
        self._reference = reference

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ImprovementReference) and self._reference == other._reference

    def __hash__(self) -> int:
        return hash(self._reference)

    def __str__(self) -> str:
        return self._reference

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._reference)})"


class Improvement:
    def __init__(self, reference: ImprovementReference, overview: ImprovementOverview):
        self._reference = reference
        self._overview = overview

    @property
    def reference(self) -> ImprovementReference:
        return self._reference

    @property
    def overview(self) -> ImprovementOverview:
        return self._overview


class ImprovementRepository:
    async def add(self, improvement: Improvement) -> None:
        raise NotImplementedError()

    async def get(self, reference: ImprovementReference) -> Improvement | None:
        raise NotImplementedError()
