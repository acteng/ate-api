from datetime import date, datetime
from enum import Enum
from typing import Self

from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.observation_types import ObservationTypeModel


class MilestoneModel(str, Enum):
    PUBLIC_CONSULTATION_COMPLETED = "public consultation completed"
    FEASIBILITY_DESIGN_STARTED = "feasibility design started"
    FEASIBILITY_DESIGN_COMPLETED = "feasibility design completed"
    PRELIMINARY_DESIGN_COMPLETED = "preliminary design completed"
    OUTLINE_DESIGN_COMPLETED = "outline design completed"
    DETAILED_DESIGN_COMPLETED = "detailed design completed"
    CONSTRUCTION_STARTED = "construction started"
    CONSTRUCTION_COMPLETED = "construction completed"
    FUNDING_COMPLETED = "funding completed"
    NOT_PROGRESSED = "not progressed"
    SUPERSEDED = "superseded"
    REMOVED = "removed"

    @classmethod
    def from_domain(cls, milestone: Milestone) -> Self:
        return cls[milestone.name]

    def to_domain(self) -> Milestone:
        return Milestone[self.name]


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: MilestoneModel
    observation_type: ObservationTypeModel
    status_date: date

    @classmethod
    def from_domain(cls, milestone: CapitalSchemeMilestone) -> Self:
        return cls(
            milestone=MilestoneModel.from_domain(milestone.milestone),
            observation_type=ObservationTypeModel.from_domain(milestone.observation_type),
            status_date=milestone.status_date,
        )

    def to_domain(self, now: datetime) -> CapitalSchemeMilestone:
        return CapitalSchemeMilestone(
            effective_date=DateTimeRange(now),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=self.status_date,
        )


class CapitalSchemeMilestonesModel(CollectionModel[CapitalSchemeMilestoneModel]):
    current_milestone: MilestoneModel | None = None
