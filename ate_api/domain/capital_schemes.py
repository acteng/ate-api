from __future__ import annotations

from ate_api.domain.dates import DateTimeRange


class CapitalScheme:
    def __init__(self, reference: str):
        self._reference = reference
        self._overviews: list[CapitalSchemeOverview] = []

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def overview(self) -> CapitalSchemeOverview:
        return next(overview for overview in self._overviews if not overview.effective_date.to)

    @property
    def overviews(self) -> list[CapitalSchemeOverview]:
        return list(self._overviews)

    def update_overview(self, overview: CapitalSchemeOverview) -> None:
        self._overviews.append(overview)


class CapitalSchemeOverview:
    def __init__(self, effective_date: DateTimeRange, bid_submitting_authority: str):
        self._effective_date = effective_date
        self._bid_submitting_authority = bid_submitting_authority

    @property
    def effective_date(self) -> DateTimeRange:
        return self._effective_date

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
