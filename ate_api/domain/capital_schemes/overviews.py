from dataclasses import dataclass
from enum import Enum, auto

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode


class CapitalSchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@dataclass(frozen=True)
class CapitalSchemeOverview:
    effective_date: DateTimeRange
    name: str
    bid_submitting_authority: AuthorityAbbreviation
    funding_programme: FundingProgrammeCode
    type: CapitalSchemeType
