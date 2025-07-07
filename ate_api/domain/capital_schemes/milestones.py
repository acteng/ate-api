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

    @property
    def is_active(self) -> bool:
        return self not in {Milestone.NOT_PROGRESSED, Milestone.SUPERSEDED, Milestone.REMOVED}

    @property
    def is_complete(self) -> bool:
        return self == Milestone.FUNDING_COMPLETED


@dataclass(frozen=True)
class CapitalSchemeMilestone:
    effective_date: DateTimeRange
    milestone: Milestone
    observation_type: ObservationType
    status_date: date


class MilestoneRepository:
    async def get_all(self, is_active: bool | None = None, is_complete: bool | None = None) -> list[Milestone]:
        raise NotImplementedError()
