from dataclasses import dataclass
from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange


class CapitalSchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@dataclass(frozen=True)
class CapitalSchemeOverview:
    effective_date: DateTimeRange
    name: str
    bid_submitting_authority: str
    funding_programme: str
    type: CapitalSchemeType


class CapitalScheme:
    def __init__(self, reference: str, overview: CapitalSchemeOverview):
        self._reference = reference
        self._overview = overview

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def overview(self) -> CapitalSchemeOverview:
        return self._overview


class CapitalSchemeRepository:
    def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    def get(self, reference: str) -> CapitalScheme | None:
        raise NotImplementedError()

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        raise NotImplementedError()
