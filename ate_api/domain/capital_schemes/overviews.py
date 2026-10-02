from dataclasses import dataclass

from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import ImprovementReference


@dataclass(frozen=True)
class CapitalSchemeOverview:
    effective_date: DateTimeRange
    name: str
    funding_programme: FundingProgrammeCode
    improvement: ImprovementReference | None
