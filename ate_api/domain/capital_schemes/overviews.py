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
