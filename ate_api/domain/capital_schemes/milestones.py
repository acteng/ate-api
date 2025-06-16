from dataclasses import dataclass
from datetime import date
from enum import IntEnum, auto

from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType


class Milestone(IntEnum):
    PUBLIC_CONSULTATION_COMPLETED = auto()
    FEASIBILITY_DESIGN_STARTED = auto()
    FEASIBILITY_DESIGN_COMPLETED = auto()
    PRELIMINARY_DESIGN_COMPLETED = auto()
    OUTLINE_DESIGN_COMPLETED = auto()
    DETAILED_DESIGN_COMPLETED = auto()
    CONSTRUCTION_STARTED = auto()
    CONSTRUCTION_COMPLETED = auto()
    FUNDING_COMPLETED = auto()
    NOT_PROGRESSED = auto()
    SUPERSEDED = auto()
    REMOVED = auto()


@dataclass(frozen=True)
class CapitalSchemeMilestone:
    effective_date: DateTimeRange
    milestone: Milestone
    observation_type: ObservationType
    status_date: date
