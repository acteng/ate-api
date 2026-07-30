from dataclasses import dataclass
from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange


class Status(Enum):
    PIPELINE = auto()
    ACTIVE = auto()
    PAUSED = auto()
    CONCLUDED = auto()
    DELETED = auto()


@dataclass(frozen=True)
class CapitalSchemeStatus:
    effective_date: DateTimeRange
    status: Status
