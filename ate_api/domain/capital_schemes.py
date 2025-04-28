from __future__ import annotations

from ate_api.domain.dates import DateTimeRange


class CapitalScheme:
    def __init__(self, reference: str, effective_date: DateTimeRange, name: str, bid_submitting_authority: str):
        self._reference = reference
        self._effective_date = effective_date
        self._name = name
        self._bid_submitting_authority = bid_submitting_authority

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


class CapitalSchemeRepository:
    def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, reference: str) -> CapitalScheme | None:
        raise NotImplementedError()

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        raise NotImplementedError()
