from dataclasses import dataclass
from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange


class CapitalSchemeBidStatus(Enum):
    SUBMITTED = auto()
    FUNDED = auto()
    NOT_FUNDED = auto()
    SPLIT = auto()
    DELETED = auto()


@dataclass(frozen=True)
class CapitalSchemeBidStatusDetails:
    effective_date: DateTimeRange
    bid_status: CapitalSchemeBidStatus
