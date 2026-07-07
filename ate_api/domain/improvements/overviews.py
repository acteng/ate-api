from dataclasses import dataclass

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange


@dataclass(frozen=True)
class ImprovementOverview:
    effective_date: DateTimeRange
    name: str
    funding_managed_by: AuthorityAbbreviation
    data_source: DataSource
    description: str | None = None
