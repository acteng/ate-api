from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange


class CapitalSchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


class CapitalScheme:
    def __init__(
        self,
        reference: str,
        effective_date: DateTimeRange,
        name: str,
        bid_submitting_authority: str,
        funding_programme: str,
        type_: CapitalSchemeType,
    ):
        self._reference = reference
        self._effective_date = effective_date
        self._name = name
        self._bid_submitting_authority = bid_submitting_authority
        self._funding_programme = funding_programme
        self._type = type_

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def effective_date(self) -> DateTimeRange:
        return self._effective_date

    @property
    def name(self) -> str:
        return self._name

    @property
    def bid_submitting_authority(self) -> str:
        return self._bid_submitting_authority

    @property
    def funding_programme(self) -> str:
        return self._funding_programme

    @property
    def type(self) -> CapitalSchemeType:
        return self._type


class CapitalSchemeRepository:
    def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, reference: str) -> CapitalScheme | None:
        raise NotImplementedError()

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        raise NotImplementedError()
