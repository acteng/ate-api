from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum, auto

from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
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
    data_source: DataSource
    surrogate_id: int | None = field(default=None, repr=False, compare=False)


class CapitalSchemeMilestones:
    def __init__(self, capital_scheme: CapitalSchemeReference):
        self._capital_scheme = capital_scheme
        self._milestones: list[CapitalSchemeMilestone] = []

    @property
    def capital_scheme(self) -> CapitalSchemeReference:
        return self._capital_scheme

    @property
    def milestones(self) -> list[CapitalSchemeMilestone]:
        return list(self._milestones)

    @property
    def current_milestone(self) -> Milestone | None:
        actual_milestones = [
            milestone.milestone
            for milestone in self._milestones
            if milestone.observation_type == ObservationType.ACTUAL
        ]
        return sorted(actual_milestones)[-1] if actual_milestones else None

    def change_milestone(self, milestone: CapitalSchemeMilestone) -> None:
        self._milestones.append(milestone)


class MilestoneRepository:
    async def get_all(self, is_active: bool | None = None, is_complete: bool | None = None) -> list[Milestone]:
        raise NotImplementedError()


class CapitalSchemeMilestonesRepository:
    async def add(self, milestones: CapitalSchemeMilestones) -> None:
        raise NotImplementedError()

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeMilestones | None:
        raise NotImplementedError()
