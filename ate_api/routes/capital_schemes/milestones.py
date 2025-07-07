from datetime import date, datetime
from enum import Enum
from typing import Annotated, Self

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ate_api.database import get_session
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone, MilestoneRepository
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.capital_schemes.milestones import DatabaseMilestoneRepository
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


router = APIRouter()


def get_milestone_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> MilestoneRepository:
    return DatabaseMilestoneRepository(session)


@router.get("/milestones", summary="Get capital scheme milestones")
async def get_milestones(
    milestones: Annotated[MilestoneRepository, Depends(get_milestone_repository)],
    is_active: Annotated[bool | None, Query(alias="active")] = None,
    is_complete: Annotated[bool | None, Query(alias="complete")] = None,
) -> CollectionModel[MilestoneModel]:
    """
    Gets the capital scheme milestones.
    """
    all_milestones = await milestones.get_all(is_active=is_active, is_complete=is_complete)

    return CollectionModel[MilestoneModel](
        items=[MilestoneModel.from_domain(milestone) for milestone in all_milestones]
    )
