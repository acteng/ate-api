from dataclasses import dataclass

from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import ImprovementReference


@dataclass(frozen=True)
class CapitalSchemeOverview:
    effective_date: DateTimeRange
    name: str
    improvement: ImprovementReference | None
